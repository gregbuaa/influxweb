from django.shortcuts import render
import urllib3
import json
from django.http import HttpResponse, JsonResponse
from .models import Influxsite,Domaininfo,Siteinfo,Tableinfo,Deviceinfo
import subprocess
import os

import time


# Create your views here.
def load_home(request):
    return render(request,'manage_index.html')



# def load_influx_state(request):
#     return render(request,"index_v1.html")

def influx_manage(request, info):
    if info == "current_state":
        contents =  influx_current_state(request)
        html_file = "current_state.html"
    elif info == "influx_sync":
        contents = influx_sync(request)
        html_file = "manage_synr.html"
    elif info == "influx_rebalance":
        contents = influx_rebalance(request)
        html_file = "manage_rebalance.html"
    elif info == "influx_recovery":
        contents = influx_recovery(request)
        html_file = "manage_recovery.html"


    return render(request,html_file, contents)

def json_manage(request,info):
    print("info",info)
    if info == "current_state":
        contents =  influx_current_state(request)
        html_file = "current_state.html"
    elif info == "influx_sync":
        contents = influx_sync(request)
        html_file = "manage_synr.html"
    elif info == "influx_rebalance":
        contents = influx_rebalance(request)
        html_file = "manage_rebalance.html"
    elif info == "influx_recovery":
        contents = influx_recovery(request)
        html_file = "manage_recovery.html"


    return JsonResponse(contents,safe=False)


def get_all_influx_site():
    influx_list = []
    has_signed = set()
    influx_table = Influxsite.objects.filter()
    for data in influx_table:
        if data.site_no in has_signed:
            continue
        has_signed.add(data.site_no)
        influx_list.append({
            "site_no":data.site_no,
            "site_name": data.site_name,
            "ip":data.ip,
            "port":str(data.port),
            "user":data.user,
            "passwd":data.passwd,
            "database":data.database,
            "chinese_name":data.site_chinese_name,
            "config_file":data.config_file
        })

    return influx_list


def influx_current_state(request):
    influx_list = get_all_influx_site()

    health_states = []

    http = urllib3.PoolManager()
    for data in influx_list:
        r = http.request('GET', 'http://%s:%s/health?stats=true&u=%s&p=%s'%((data["ip"],data["port"],data["user"],data["passwd"]))) ## ip后面会从MySQL配置表中取出来！
        current = json.loads(r.data.decode('utf-8'))

        for circle in current:
            circle['circle']['site_name'] = data['chinese_name']+data['site_name'] 

        health_states += current
    contents = {
        "health_state":health_states
    }
    

    return  contents


def influx_sync(request):
    influx_list = get_all_influx_site()

    site_list = []

    http = urllib3.PoolManager()
    max_cicrle = 10
    sync_info = []
    for data in influx_list:
        r = http.request('GET', 'http://%s:%s/transfer/state?u=%s&p=%s'%(data["ip"],data["port"],data["user"],data["passwd"])) ## ip后面会从MySQL配置表中取出来！
        states = json.loads(r.data.decode('utf-8'))
        site_list.append({
                "site_no":str(data["site_no"]),
                "site_name":data["site_name"],
                "chinese_name":data["chinese_name"],
                "states":str(states["resyncing"])
            }
        )
        for i in range(max_cicrle):
            r = http.request('GET', 'http://%s:%s/transfer/stats?circle_id=%d&type=resync&u=%s&p=%s'%(data["ip"],data["port"],i,data["user"],data["passwd"])) ## ip后面会从MySQL配置表中取出来！
            circle = json.loads(r.data.decode('utf-8'))
            if "error" in circle:
                break
            circle["site_no"] = "站点"+data["chinese_name"]+ data["site_name"] + "的第"+str(i+1)+"个cicrle"
            sync_info.append(circle)

    
    has_sync = {}
    for data in sync_info:
        for urlname, meta in data.items():
            if "http" not in urlname:
                continue
            if meta['database_total'] != meta['database_done']:
                has_sync[urlname] = False
                continue
            if meta['measurement_total'] != meta['measurement_done']:
                has_sync[urlname] = False
                continue

            has_sync[urlname] = True


    contents = {
        "site_list":site_list,
        "sync_state": sync_info,
        "has_sync":has_sync
    }

    print(contents)

    # return render(request,'manage_synr.html',contents)
    return contents


INFLUX_PROXY_CONFIG_PATH = r"/home/zeal/project/influx-proxy/"


def influx_rebalance(request):
    influx_list = get_all_influx_site()
    http = urllib3.PoolManager()
    max_cicrle = 10
    sync_info = []
    site_list = []
    for data in influx_list:
        with open(INFLUX_PROXY_CONFIG_PATH + data["config_file"],"r") as f:
            proxy_config = json.load(f)
            for circle in proxy_config["circles"]:
                for backend in circle['backends']:
                    backend["auth_secure"] = str(backend["auth_secure"])
            # print(proxy_config)

        r = http.request('GET', 'http://%s:%s/transfer/state?u=%s&p=%s'%(data["ip"],data["port"],data["user"],data["passwd"])) ## ip后面会从MySQL配置表中取出来！
        states = json.loads(r.data.decode('utf-8'))
        transferring = False
        for element in states["circles"]:
            if element["transferring"]:
                transferring = True
                break

        site_list.append({
                "site_no":str(data["site_no"]),
                "site_name":data["site_name"],
                "chinese_name":data["chinese_name"],
                "states":str(transferring),
                "config_file": proxy_config
            }
        )
        for i in range(max_cicrle):
            r = http.request('GET', 'http://%s:%s/transfer/stats?circle_id=%d&type=rebalance&u=%s&p=%s'%(data["ip"],data["port"],i,data["user"],data["passwd"])) ## ip后面会从MySQL配置表中取出来！
            circle = json.loads(r.data.decode('utf-8'))
            if "error" in circle:
                break
            circle["site_no"] = "站点"+data["chinese_name"]+ data["site_name"] + "的第"+str(i+1)+"个cicrle"
            sync_info.append(circle)
    
    has_sync = {}
    for data in sync_info:
        for urlname, meta in data.items():
            if "http" not in urlname:
                continue
            if meta['database_total'] != meta['database_done']:
                has_sync[urlname] = False
                continue
            if meta['measurement_total'] != meta['measurement_done']:
                has_sync[urlname] = False
                continue

            has_sync[urlname] = True



    contents = {
        "site_list":site_list,
        "sync_state": sync_info,
        "has_sync":has_sync
    }

    return contents


def influx_recovery(request):

    proxy_config = '''{
    "circles": [
        {
            "name": "circle-1",
            "backends": [
                {
                    "name": "influxdb-1-1",
                    "url": "http://127.0.0.1:14001",
                    "username": "",
                    "password": "",
                    "auth_secure": false
                },
                {
                    "name": "influxdb-1-2",
                    "url": "http://127.0.0.1:14002",
                    "username": "",
                    "password": "",
                    "auth_secure": false
                }
            ]
        },
        {
            "name": "circle-2",
            "backends": [
                {
                    "name": "influxdb-2-1",
                    "url": "http://127.0.0.1:14003",
                    "username": "",
                    "password": "",
                    "auth_secure": false
                },
                {
                    "name": "influxdb-2-2",
                    "url": "http://127.0.0.1:14004",
                    "username": "",
                    "password": "",
                    "auth_secure": false
                }
            ]
        }
    ],
    "listen_addr": ":7920",
    "db_list": [],
    "data_dir": "data",
    "tlog_dir": "log",
    "hash_key": "idx",
    "flush_size": 10000,
    "flush_time": 1,
    "check_interval": 1,
    "rewrite_interval": 10,
    "conn_pool_size": 20,
    "write_timeout": 10,
    "idle_timeout": 10,
    "username": "",
    "password": "",
    "auth_secure": false,
    "write_tracing": false,
    "query_tracing": false,
    "https_enabled": false,
    "https_cert": "",
    "https_key": ""
    }
    '''

    http = urllib3.PoolManager()
    max_cicrle = 10

    sync_info = []
    for i in range(max_cicrle):
        r = http.request('GET', 'http://192.168.231.200:7920/transfer/stats?circle_id=%d&type=recovery'%(i)) ## ip后面会从MySQL配置表中取出来！
        circle = json.loads(r.data.decode('utf-8'))
        if "error" in circle:
            break
        sync_info.append(circle)

    
    has_sync = {}


    for data in sync_info:
        for urlname, meta in data.items():
            if meta['database_total'] != meta['database_done']:
                has_sync[urlname] = False
                continue
            if meta['measurement_total'] != meta['measurement_done']:
                has_sync[urlname] = False
                continue

            has_sync[urlname] = True

    contents = {
        "sync_state": sync_info,
        "has_sync":has_sync,
        "proxy_config":json.loads(proxy_config)
    }

    return contents


def data_sync(request):
    tick = request.GET.get('from_timestap', '0')
    worker_num = request.GET.get('worker_num', '4')
    site_no = request.GET.get("site_no","0")
    site_no = str(site_no)
    http = urllib3.PoolManager()
    ## tick接口：所有 circle 互相同步从 <tick> 时间点开始（10位时间戳，包含该点）的数据，默认为 0，表示同步所有历史数据，暂不实现
    site_info = Influxsite.objects.get(site_no = int(site_no))

    r = http.request('POST','http://%s:%s/resync?u=%s&p=%s&worker=%s'%(site_info.ip, str(site_info.port),site_info.user, site_info.passwd, worker_num))

    response_state = r.data.decode('utf-8')
    # response_state = "accepted"
    content= {
        "response_state":response_state
    }

    # print("accept"+response_state)

    return JsonResponse(content,safe=False)


def data_rebalance(request):
    circle_select = request.POST.get('circle_select', 'circle-1')
    table_content = request.POST.get('table_content', "[]")
    site_no = request.POST.get("site_no","1")

    table_content = json.loads(table_content)
    http = urllib3.PoolManager()

    # rebalance代码
    ## 修改proxy.json实例，增删实例
    site_info = Influxsite.objects.get(site_no = int(site_no))
    with open(INFLUX_PROXY_CONFIG_PATH + site_info.config_file,"r") as f:
        proxy_config = json.load(f)

    new_circle_config = []
    
    operator_symbol = "add" 

    print(table_content)
    for data in table_content:
        if "checkbox" in data and data["checkbox"]==True:
            operator_symbol = "rm"
            continue
        new_circle_config.append({
            "name":data["name"],
            "url":data["url"],
            "username":data["username"],
            "password":data["password"],
            "auth_secure": False if data['auth_secure'] == "False" else True
        })

    response_state = "accepted"

    # if len(new_circle_config) == len(proxy_config["circles"]):
    #     response_state = "not accept"
    #     print(True)

    if response_state != "not accept":
        ## 重启influx proxy
        circle_id = 0
        for count, circle in enumerate(proxy_config["circles"]):
            if circle["name"] == circle_select:
                circle["backends"] = new_circle_config
                circle_id = count
            

        proxy_text = json.dumps(proxy_config,indent=4)
        print(proxy_text)

        with open(INFLUX_PROXY_CONFIG_PATH + site_info.config_file,"w") as f:
            f.write(proxy_text)

        ## 调用这个命令来做
        # ps -ef|grep hello|grep -v grep|cut -c 9-15 | xargs kill -9
        rc = subprocess.check_call(r'ps -ef|grep %s|grep -v grep|cut -c 9-15 | xargs kill -9'%(site_info.config_file), shell=True)
        print("rc",rc)
        os.chdir(INFLUX_PROXY_CONFIG_PATH)
        rc2 =  subprocess.check_call(r'nohup ./influx-proxy -config %s &'%(site_info.config_file), shell=True)
        print("rc2",rc2)

        time.sleep(2)
        ## 调用接口/reblalance完成操作
        r = http.request('POST','http://%s:%s/rebalance?circle_id=%d&operation=%s&worker=4&u=%s&p=%s'%(site_info.ip, str(site_info.port), circle_id, operator_symbol, site_info.user,site_info.passwd))
        response_state = r.data.decode('utf-8')
        ## 状态查询

    content= {
        "response_state":response_state
    }

    print("扩容命令已经发出！！！")
    return JsonResponse(content,safe=False)


def data_recovery(request):

    to_circle = request.POST.get('to_circle', 'circle-1')
    from_circle = request.POST.get('from_circle', 'circle-1')
    worker_num = request.POST.get('worker_num', '4')
    recovery_influx = request.POST.get('recovery_influx', '')
    table_content = request.POST.get('table_content', "[]")

    table_json = json.loads(table_content)
    new_table_json = []
    for item in table_json:
        if 'checkbox' in item and item['checkbox']==True:
            ## 删除的坏的influxdb实例，从proxy.json文件中拿掉
            continue
        if 'checkbox' in item:
            del item['checkbox']
        new_table_json.append(item)

    ##恢复代码
    ## 根据table_content修改proxy.json
    PROXY_DIR = ""
    reader = open(PROXY_DIR, 'r')
    orignal_proxy = json.load(reader)
    
    new_circles = []
    to_circle_id = -1
    from_circle_id = -1
    for index, circle in enumerate(orignal_proxy['circles']):
        if circle['name'] == to_circle:
            new_circles.append({
                'name':to_circle,
                'backends': new_table_json
            })
            to_circle_id = index
            continue
        if circle['name'] == from_circle:
            from_circle_id = index
        
        new_circles.append(circle)

    orignal_proxy['circles'] = new_circles
    ## 重启所有的influx proxy


    ## 根据接口/recovery进行操作 
    http = urllib3.PoolManager()
    r = http.request('POST','http://192.168.231.200:7920/recovery?from_circle_id=%d&to_circle_id=%d&worker=%s&backend_urls=%s'%(from_circle_id,to_circle_id,worker_num,recovery_influx))
    response_state = r.data.decode('utf-8')

    # response_state = "accepted"
    content= {
        "response_state":response_state
    }
    return JsonResponse(content,safe=False)


