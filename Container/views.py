from django.http import JsonResponse
from django.shortcuts import render

# Create your views here.
import docker
from django.views.decorators.csrf import csrf_exempt

client = docker.from_env()


def ctn_list():
    # client = docker.APIClient(base_url='tcp://10.251.255.171:2375')
    containers = client.containers.list(all=True)
    res = []
    print(containers[0].__dict__)

    for container in containers:
        # image = client.images.get(container.attrs['Image'])
        res.append({
            'id': container.attrs['Id'],
            'name': container.attrs['Name'],
            'image_id': container.attrs['Image'],
            'status': container.attrs['State']['Status'],
            'ports': container.ports,
            'start_at': container.attrs['State']['StartedAt']},
        )

    return res

def ctn_get(container_id):
    container = client.containers.get(container_id)
    container_attr = {}
    container_attr['id'] = container.id
    container_attr['created'] = container.attrs['Created']
    container_attr['port'] = container.attrs['HostConfig']['PortBindings']
    try:
        for key in container_attr['port'].keys():
            container_attr['port'][key] = container_attr['Port'][key][0]['HostPort']
    except:
        container_attr['port'] = {}
    try:
        container_attr['image'] = container.image.tags[0]
    except:
        container_attr['Image'] = 'unknown'
    container_attr['name'] = container.name
    container_attr['status'] = container.status

    return container_attr



@csrf_exempt
def list_containers(request):
    res = ctn_list()
    return JsonResponse({'status': 0, 'res': res})

@csrf_exempt
def get_container(request):
    container_id = request.GET.get('ctn_id')
    res = ctn_get(container_id)
    return JsonResponse({'status': 0, 'res': res})