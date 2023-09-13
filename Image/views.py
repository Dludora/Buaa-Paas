from django.shortcuts import render

# Create your views here.
import docker
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from functools import wraps

client = docker.from_env()


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

def image_list():
    images = client.images.list(all=True)
    res = []
    for image in images:
        res.append({
            'id': image.attrs['Id'],
            'tags': image.tags,
            'short_id': image.short_id,
            'created': image.attrs['Created'],
            'size': image.attrs['Size']
        })
    return res


def image_detail(image_id):
    image = client.images.get(image_id)
    res = {
        'id': image.id,
        'tags': image.tags,
        'short_id': image.short_id,
        'created': image.attrs['Created'],
        'size': image.attrs['Size'],
        'container_id': image.attrs['Container'],
        'exposed_ports': image.attrs['Config']['ExposedPorts'],
    }

    return res


def image_remove(image_id):
    res = client.images.remove(image_id)
    return {'status': 0}


def image_build(fileobj, tag):
    try:
        image, res = client.images.build(fileobj=fileobj, tag=tag, custom_context=True)
        return {'status': 0}
    except:
        return {'status': -1}


@csrf_exempt
@error_catch
def list_images(request):
    res = image_list()

    return JsonResponse({'status': 0, 'res': res})


@csrf_exempt
@error_catch
def get_image_detail(request):
    image_id = request.GET.get('id')
    res = image_detail(image_id)

    return JsonResponse({'res': res})


@csrf_exempt
@error_catch
def remove_image(request):
    name = request.GET.get('id')
    res = image_remove(name)

    return JsonResponse({'status': 0, 'res': res})


@csrf_exempt
@error_catch
def build_image(request):
    fileobj = request.FILES.get('fileobj')
    tag = request.POST.get('tag')
    res = image_build(fileobj, tag)

    return JsonResponse({'res': res})
