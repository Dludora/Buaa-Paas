from .views import *
from django.urls import path

urlpatterns = [
    path('create', create_app),
    path('list', get_applications),
    path('get_services', get_svcs_of_app),
    path('delete_service', delete_service),
    path('delete', delete_application)
]