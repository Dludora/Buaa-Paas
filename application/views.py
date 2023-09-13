import time
from functools import wraps
from os import path
import yaml
import os
import random
from kubernetes import client, config
from kubernetes.client import ApiException
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse

image_prefix = ""

# Create your views here.

def error_catch(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        try:
            result = function(*args, **kwargs)
            return result
        except Exception as e:
            return JsonResponse({'status': -1, 'msg': str(e)})
        # try:
        #     return function(*args)
        # except:
        #     return JsonResponse({'status': -1})
    return wrapper


def getPort():
    pscmd = "netstat -ntl |grep -v Active| grep -v Proto|awk '{print $4}'|awk -F: '{print $NF}'"
    procs = os.popen(pscmd).read()
    procarr = procs.split("\n")
    tt = random.randint(30000, 32000)
    if tt not in procarr:
        return tt
    else:
        getPort()


@csrf_exempt
@error_catch
def create_app(request):
    config.load_kube_config(config_file="./application/configRep/kubeconfig.yaml")
    app_name = request.GET['app_name']
    try:
        with open(path.join(path.dirname(__file__), "./configRep/namespace.yaml")) as f:
            dep = yaml.safe_load(f)
            dep["metadata"]["name"] = app_name
            k8s_core_v1 = client.CoreV1Api()
            k8s_core_v1.create_namespace(body=dep)
    except ApiException as e:
        res = {"status": -1}
        return JsonResponse(res)
    res = {"status": 0}
    return JsonResponse(res)


# 获取应用列表(经测试可用)
@csrf_exempt
@error_catch
def get_applications(request):
    config.load_kube_config(config_file="./application/configRep/kubeconfig.yaml")
    v1 = client.CoreV1Api()
    app_list = []
    for ns in v1.list_namespace().items:
        if (ns.metadata.name != "kube-system" and ns.metadata.name != "kube-public" and ns.metadata.name != "default"
                and ns.metadata.name != "kube-node-lease" and ns.metadata.name != "kubernetes-dashboard"):
            app = {}
            app['name'] = ns.metadata.name
            app['status'] = ns.status.phase
            app['created_time'] = str(ns.metadata.creation_timestamp)
            app_list.append(app)
    return JsonResponse({"status": 0, "res": app_list})


# 在某个应用下以某个镜像创建服务
@csrf_exempt
@error_catch
def create_service(request):
    svc_name = request.GET['svc_name']
    app_name = request.GET['app_name']
    img_name = request.GET['img_name']
    try:
        config.load_kube_config(config_file="./application/configRep/kubeconfig.yaml")
        with open(path.join(path.dirname(__file__), "./configRep/deploy.yaml")) as f:
            dep = yaml.safe_load(f)
            dep["metadata"]["name"] = svc_name
            dep["spec"]["template"]["metadata"]["labels"]["run"] = svc_name
            dep["spec"]["selector"]["matchLabels"]["run"] = svc_name
            dep["spec"]["template"]["spec"]["containers"][0]["name"] = img_name
            dep["spec"]["template"]["spec"]["containers"][0]["image"] = image_prefix + img_name
            k8s_apps_v1 = client.AppsV1Api()
            resp = k8s_apps_v1.create_namespaced_deployment(namespace=app_name, body=dep)
        time.sleep(2)
        with open(path.join(path.dirname(__file__), "./configRep/service.yaml")) as f:
            dep = yaml.safe_load(f)
            dep["metadata"]["name"] = svc_name
            dep["metadata"]["labels"]["svc"] = svc_name + "-svc"
            dep["spec"]["ports"][0]["nodePort"] = getPort()
            dep["spec"]["selector"]["run"] = svc_name
            k8s_core_v1 = client.CoreV1Api()
            resp = k8s_core_v1.create_namespaced_service(namespace=app_name, body=dep)
    except ApiException as e:
        res = {"status": -1}
        return JsonResponse(res)
    res = {"status": 0}
    return JsonResponse(res)


# 获取某个应用的服务(经测试可用)
@csrf_exempt
@error_catch
def get_svcs_of_app(request):
    config.load_kube_config(config_file="./application/configRep/kubeconfig.yaml")
    v1 = client.CoreV1Api()
    app_name = request.GET['app_name']
    svcs = v1.list_namespaced_service(namespace=app_name)
    svc_list = []
    for i in svcs.items:
        svc = {"namespace": i.metadata.namespace, "name": i.metadata.name, "service": i.spec.selector,
               "uid": i.metadata.uid,
               "create_time": str(i.metadata.creation_timestamp),
               "cluster_ip": i.spec.cluster_ip, "type": i.spec.type,
               }
        if i.spec.selector is not None: svc["service"]=i.spec.selector["run"]
        if i.spec.ports[0].node_port is not None:
            svc["port"]=str(i.spec.ports[0].port)+":"+str(i.spec.ports[0].node_port)+"/"+str(i.spec.ports[0].protocol)
        svc_list.append(svc)
    return JsonResponse({"status": 0, "res": svc_list})


# 删除某个应用下的某个服务（经测试可用）
@csrf_exempt
@error_catch
def delete_service(request):
    svc_name = request.GET['svc_name']
    app_name = request.GET['app_name']
    config.load_kube_config(config_file="./application/configRep/kubeconfig.yaml")
    k8s_core_v1 = client.CoreV1Api()
    k8s_apps_v1 = client.AppsV1Api()
    try:
        resp = k8s_core_v1.delete_namespaced_service(namespace=app_name, name=svc_name)
        resp1 = k8s_apps_v1.delete_namespaced_deployment(namespace=app_name, name=svc_name)
    except ApiException as e:
        res = {"status": -1}
        return JsonResponse(res)
    res = {"status": 0}
    return JsonResponse(res)


# 删除应用和其中的所有服务（经测试可用）
@csrf_exempt
@error_catch
def delete_application(request):
    app_name = request.GET['app_name']
    config.load_kube_config(config_file="./application/configRep/kubeconfig.yaml")
    k8s_core_v1 = client.CoreV1Api()
    try:
        resp = k8s_core_v1.delete_namespace(name=app_name)
    except ApiException as e:
        res = {"status": -1}
        return JsonResponse(res)
    res = {"status": 0}
    return JsonResponse(res)