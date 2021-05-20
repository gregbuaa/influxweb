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
    path('',views.load_home, name="manage_home"),
    path('subscribe', views.influx_subscribe, name="influx_subscribe"),
    path('post/<str:info>/',views.influx_manage, name="influx_manage"),
    path('data_subscribe',views.data_subscribe, name="data_subscribe"),
    path('data_sync',views.data_sync, name="data_sync"),
    path('data_rebalance',views.data_rebalance, name="data_rebalance"),
    path('data_recovery',views.data_recovery, name="data_recovery"),
    path('json/<str:info>/', views.json_manage, name="json_manage")
]
