"""influxweb URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path, include
from . import views
from login.utils import login_required

urlpatterns = [
    path('',login_required(views.load_home), name="manage_home"),
    path('subscribe', login_required(views.influx_subscribe), name="influx_subscribe"),
    path('post/<str:info>/',login_required(views.influx_manage), name="influx_manage"),
    path('data_subscribe',login_required(views.data_subscribe), name="data_subscribe"),
    path('data_sync',login_required(views.data_sync), name="data_sync"),
    path('data_rebalance',login_required(views.data_rebalance), name="data_rebalance"),
    path('data_recovery',login_required(views.data_recovery), name="data_recovery"),
    path('json/<str:info>/', login_required(views.json_manage), name="json_manage")
]
