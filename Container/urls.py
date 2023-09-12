# -*- coding: utf-8 -*-
# @Time    : 2023/9/12 20:58
# @Author  : Dludora
# @Require : 
# @File    : urls.py
# @Software: PyCharm

from .views import *
from django.urls import path

urlpatterns = [
    path('list', list_containers)
]
