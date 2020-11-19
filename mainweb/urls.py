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
    path('',login_required(views.load_home), name="home"),
    path('load_tables_info',views.load_tables_info,name='load_tables_info'),
    path('load_site_table',views.load_site_table,name='load_site_table'),
    path('load_config_table',views.load_config_table,name='load_config_table'),
    path('save_config_tables',views.save_config_tables,name='save_config_tables'),
    path('del_config_tables',views.del_config_tables,name='del_config_tables'),
    path('save_influx_tables',views.save_influx_tables,name='save_influx_tables')
]
