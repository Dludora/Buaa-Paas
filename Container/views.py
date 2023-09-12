from django.http import JsonResponse
from django.shortcuts import render

# Create your views here.
import docker
from django.views.decorators.csrf import csrf_exempt


def ctn_list():
    client = docker.APIClient(base_url='tcp://10.251.255.171:2375')
    containers = client.containers.list(all=True)
    res = []
    for container in containers:
        res.append(container)

    return res


@csrf_exempt
def list_containers(request):
    # if request.method == 'Get':

    res = ctn_list()
    return JsonResponse({'status': 0, 'res': res})


