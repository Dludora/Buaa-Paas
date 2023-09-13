from .views import *
from django.urls import path

urlpatterns = [
    path('list', list_images),
    path('detail', get_image_detail),
    path('remove', remove_image),
    path('build', build_image),
]