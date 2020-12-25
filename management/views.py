from django.shortcuts import render
import urllib3
import json



# Create your views here.
def load_home(request):
    return render(request,'manage_index.html')



# def load_influx_state(request):
#     return render(request,"index_v1.html")

def influx_manage(request, info):
    if info == "current_state":
        return influx_current_state(request)
    elif info == "influx_sync":
        return influx_sync(request)
    elif info == "influx_rebalance":
        return influx_rebalance(request)
    elif info == "influx_recovery":
        return influx_recovery(request)

    # if info == "current_state":
    #     return render(request, "current_state.html")


    return render(request,"index_v1.html")


def influx_current_state(request):
    http = urllib3.PoolManager()
    r = http.request('GET', 'http://219.224.169.20:7920/health?stats=true') ## ip后面会从MySQL配置表中取出来！
    health_state = json.loads(r.data.decode('utf-8'))

    contents = {
        "health_state":health_state
    }

    # print(health_state)

    return render(request,'current_state.html',contents)


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

    return render(request,'manage_synr.html',contents)



def influx_rebalance(request):
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
        "has_sync":has_sync
    }

    return render(request,'manage_rebalance.html',contents)


def influx_recovery(request):

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
        "has_sync":has_sync
    }

    return render(request,'manage_recovery.html',contents)



