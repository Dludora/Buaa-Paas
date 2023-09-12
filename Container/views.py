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
            'id': container.id,
            'name': container.name,
            'image_id': container.attrs['Image'],
            'status': container.attrs['State']['Status'],
            'ports': container.attrs['NetworkSettings']['Ports'],
            'start_at': container.attrs['State']['StartedAt']},
        )

    return res

def ctn_get(container_id):
    container = client.containers.get(container_id)
    container_attr = {}
    container_attr['id'] = container.id
    



@csrf_exempt
def list_containers(request):
    # if request.method == 'Get':

    res = ctn_list()
    return JsonResponse({'status': 0, 'res': res})

