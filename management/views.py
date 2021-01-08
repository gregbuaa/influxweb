from django.shortcuts import render
import urllib3
import json
from django.http import HttpResponse, JsonResponse


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


def influx_current_state(request):
    http = urllib3.PoolManager()
    r = http.request('GET', 'http://219.224.169.20:7920/health?stats=true') ## ip后面会从MySQL配置表中取出来！
    health_state = json.loads(r.data.decode('utf-8'))

    contents = {
        "health_state":health_state
    }

    return  contents


def influx_sync(request):
    http = urllib3.PoolManager()
    max_cicrle = 10

    sync_info = []
    for i in range(max_cicrle):
        r = http.request('GET', 'http://219.224.169.20:7920/transfer/stats?circle_id=%d&type=resync'%(i)) ## ip后面会从MySQL配置表中取出来！
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
        "has_sync":has_sync
    }

    print(contents)

    # return render(request,'manage_synr.html',contents)
    return contents



def influx_rebalance(request):
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
        r = http.request('GET', 'http://219.224.169.20:7920/transfer/stats?circle_id=%d&type=rebalance'%(i)) ## ip后面会从MySQL配置表中取出来！
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

    # return render(request,'manage_rebalance.html',contents)
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
        r = http.request('GET', 'http://219.224.169.20:7920/transfer/stats?circle_id=%d&type=recovery'%(i)) ## ip后面会从MySQL配置表中取出来！
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
    http = urllib3.PoolManager()
    ## tick接口：所有 circle 互相同步从 <tick> 时间点开始（10位时间戳，包含该点）的数据，默认为 0，表示同步所有历史数据，暂不实现
    r = http.request('POST','http://219.224.169.20:7920/resync?worker=%s'%(worker_num))

    response_state = r.data.decode('utf-8')
    # response_state = "accepted"
    content= {
        "response_state":response_state
    }

    # print("accept"+response_state)

    return JsonResponse(content,safe=False)


def data_rebalance(request):
    circle_select = request.POST.get('circle_select', 'circle-1')
    table_content = request.POST.get('table_content', "{}")

    ## rebalance代码
    ## 修改proxy.json实例，增删实例

    ## 重启influx proxy

    ## 调用接口/reblalance完成操作

    ## 状态查询



    print(circle_select)
    print("table_content",table_content)
    response_state = "accepted"
    content= {
        "response_state":response_state
    }
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
    r = http.request('POST','http://219.224.169.20:7920/recovery?from_circle_id=%d&to_circle_id=%d&worker=%s&backend_urls=%s'%(from_circle_id,to_circle_id,worker_num,recovery_influx))
    response_state = r.data.decode('utf-8')

    # response_state = "accepted"
    content= {
        "response_state":response_state
    }
    return JsonResponse(content,safe=False)


