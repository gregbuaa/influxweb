from django.shortcuts import render
import urllib3
import json
from django.http import HttpResponse, JsonResponse
from .models import Influxsite,Domaininfo,Siteinfo,Tableinfo,Deviceinfo
import subprocess
import os
from influxdb import InfluxDBClient
from django.db.models import Q

import time


# Create your views here.
def load_home(request):
    return render(request,'manage_index.html')



def influx_subscribe(request):
    influx_table = Influxsite.objects.filter()


    proxy_info = []
    node_info = {}
    for proxy in influx_table:
        info = {
                "site_no": str(proxy.site_no),
                "site_name":proxy.site_name,
                "site_chinese_name":proxy.site_chinese_name,
                "site_ip":proxy.ip,
                "site_port":proxy.port,
                "database_chinese_name":proxy.database_chinese_name
            }
        if proxy.influx_type=="proxy":
            info["subscribe"]=proxy.subscribe.split(",")
            proxy_info.append(info)
        else:
            site_no = str(proxy.site_no)
            if site_no not in node_info:
                node_info[site_no] = []
            node_info[site_no].append(info)

    for proxy in proxy_info:
        if proxy['site_no'] in node_info:
            proxy['node_info'] = node_info[proxy['site_no']]
            # proxy['node_info']['bel']


    influx_subject = Siteinfo.objects.filter()
    subject_info = []
    for site in influx_subject:
        subject_info.append({
            "id": site.id,
            "site_chinese_name":site.site_chinese_name,
            "site_name":site.site_name
        })


    contents = {
        "proxy_info":proxy_info,
        "subject_info":subject_info
    }

    return render(request,"manage_subscribe.html", contents)



def write_influx_data(client, table_name, all_update_data):
    table_attrs = Domaininfo.objects.filter(table_name=table_name)
    title_name = {}
    title_name['fields'] = []
    title_name['tags'] = []
    for attr in table_attrs: 
        if attr.domaintype == "field":
            title_name['fields'].append(attr.domain_name)
        elif attr.domaintype == "tag":
            title_name['tags'].append(attr.domain_name)
        elif attr.domaintype == "datetime":
            title_name['time'] = attr.domain_name

    try:
        bodys = []
        for data in all_update_data:
            body = {}
            body['measurement'] = table_name
            if title_name['time'] in data:
                if data[title_name['time']] !='':
                    if 'T' in data[title_name['time']]:
                        timestamp = data[title_name['time']]
                    else:
                        timestamp = datetime.datetime.strptime(data[title_name['time']], '%Y-%m-%d %H:%M:%S').isoformat("T")+"Z"
                    body['time'] = timestamp
            body['tags'] = {}
            body['fields'] = {}
            for tag in title_name['tags']:
                body['tags'][tag] = data[tag]
            for field in title_name['fields']:
                if data[field] == "":
                    data[field] = '0.0'
                body['fields'][field] = float(data[field])
            bodys.append(body)

        res = client.write_points(bodys)
        update_state = 1
        update_info = "更新成功！"
    except Exception  as e:
        print(e)
        update_state = 0
        update_info = "更新失败！请检查数据格式！"

    return update_state, update_info


def data_subscribe(request):
    new_subjects = request.GET.get('new_subjects', '[]')
    new_name = request.GET.get('new_name', '4')
    site_no = request.GET.get("site_no","0")
    site_no = str(site_no)

    original_subscribe = Influxsite.objects.get(site_no=site_no,influx_type="proxy").subscribe

    new_subjects = json.loads(new_subjects)
    subscribe_str=",".join(new_subjects)
    print(subscribe_str)
    if new_subjects == []:
        Influxsite.objects.filter(site_no=site_no,influx_type="proxy").update(site_chinese_name=new_name)
    else:
        Influxsite.objects.filter(site_no=site_no,influx_type="proxy").update(site_chinese_name=new_name,subscribe=subscribe_str)

    response_state = True
    message = "设置完毕"
    ## 启动时的同步管理！！！根据订阅的主题，拉取一条最新的记录进入到INFLUXDB当中。
    if original_subscribe != subscribe_str:
        current_site_list = new_subjects
        original_site_list = original_subscribe.split(',')

        new_sites = []
        for site in current_site_list:
            if site not in original_subscribe:
                new_sites.append(site)

        currentinflux = Influxsite.objects.get(influx_type="proxy",site_no=site_no)
        currentclient = InfluxDBClient(host=currentinflux.ip,port=currentinflux.port,username=currentinflux.user,password=currentinflux.passwd,database=currentinflux.database)

        for site in new_sites:
            allinflux = Influxsite.objects.filter(influx_type="proxy",subscribe__contains=site).exclude(site_no=site_no)
            print("allinflux",allinflux)
            if allinflux == None:
                message = "不包含站点%s信息，无法初始化同步！！！"

            for site_info in allinflux:
                if site_info.site_no == site_no:
                    continue
                ### 连接到代理上去
                client = InfluxDBClient(host=site_info.ip,port=site_info.port,username=site_info.user,password=site_info.passwd,database=site_info.database)
                ### 插入一条新的数据即可。
                result_telem = client.query("select * from telemetry where site_name='%s' order by time desc LIMIT 5"%(site))
                result_teles = client.query("select * from telesignalling where site_name='%s' order by time desc LIMIT 5"%(site))
                result_telem = list(result_telem.get_points(measurement="telemetry"))
                result_teles = list(result_teles.get_points(measurement="telesignalling"))
                write_influx_data(currentclient, "telemetry", result_telem)
                write_influx_data(currentclient, "telesignalling", result_teles)
                

    ## 状态查询
    content= {
        "response_state":True
    }

    return JsonResponse(content,safe=False)



# def load_influx_state(request):
#     return render(request,"index_v1.html")

def influx_manage(request, info):
    if info == "current_state":
        contents =  influx_current_state(request)
        html_file = "current_state.html"
    elif info == "influx_sync":
        contents = influx_return(request, "resync")
        html_file = "manage_synr.html"
    elif info == "influx_rebalance":
        contents = influx_return(request, "rebalance")
        html_file = "manage_rebalance.html"
    elif info == "influx_recovery":
        contents = influx_return(request, "recovery")
        html_file = "manage_recovery.html"


    return render(request,html_file, contents)

def json_manage(request,info):
    print("info",info)
    if info == "current_state":
        contents =  influx_current_state(request)
        html_file = "current_state.html"
    elif info == "influx_sync":
        contents = influx_return(request, "sync")
        html_file = "manage_synr.html"
    elif info == "influx_rebalance":
        contents = influx_return(request, "rebalance")
        html_file = "manage_rebalance.html"
    elif info == "influx_recovery":
        contents = influx_return(request, "recovery")
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


INFLUX_PROXY_CONFIG_PATH = r"/home/zeal/project/influx-proxy/"
def influx_return(request, order):
    influx_list = get_all_influx_site()
    http = urllib3.PoolManager()
    max_cicrle = 10
    sync_info = []
    site_list = []

    
    for data in influx_list:
        r = http.request('GET', 'http://%s:%s/transfer/state?u=%s&p=%s'%(data["ip"],data["port"],data["user"],data["passwd"])) ## ip后面会从MySQL配置表中取出来！
        states = json.loads(r.data.decode('utf-8'))

        if order == "rebalance" or order == "recovery": 
            with open(INFLUX_PROXY_CONFIG_PATH + data["config_file"],"r") as f:
                proxy_config = json.load(f)
                for circle in proxy_config["circles"]:
                    for backend in circle['backends']:
                        backend["auth_secure"] = str(backend["auth_secure"])
            transferring = "False"
            for element in states["circles"]:
                if element["transferring"]:
                    transferring = "True"
                    break
        else:
            proxy_config = {}
            transferring = str(states["resyncing"])


        site_list.append({
                "site_no":str(data["site_no"]),
                "site_name":data["site_name"],
                "chinese_name":data["chinese_name"],
                "states":str(transferring),
                "config_file": proxy_config
            }
        )
        for i in range(max_cicrle):
            r = http.request('GET', 'http://%s:%s/transfer/stats?circle_id=%d&u=%s&p=%s&type=%s'%(data["ip"],data["port"],i,data["user"],data["passwd"],order)) ## ip后面会从MySQL配置表中取出来！
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

def data_sync(request):
    tick = request.GET.get('from_timestap', '0')
    worker_num = request.GET.get('worker_num', '4')
    site_no = request.GET.get("site_no","0")
    site_no = str(site_no)
    http = urllib3.PoolManager()
    ## tick接口：所有 circle 互相同步从 <tick> 时间点开始（10位时间戳，包含该点）的数据，默认为 0，表示同步所有历史数据，暂不实现
    site_info = Influxsite.objects.get(site_no = int(site_no), influx_type='proxy')

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
    site_info = Influxsite.objects.get(site_no = int(site_no), influx_type='proxy')
    with open(INFLUX_PROXY_CONFIG_PATH + site_info.config_file,"r") as f:
        proxy_config = json.load(f)

    new_circle_config = []
    
    operator_symbol = "add" 

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
    to_circle = request.POST.get('to_circle', 'circle_1')
    from_circle = request.POST.get('from_circle', 'circle_2')
    worker_num = request.POST.get('worker_num', '4')
    recovery_influx = request.POST.get('recovery_influx', '')
    table_content = request.POST.get('table_content', "[]")
    site_no = request.POST.get("site_no","1")

    table_content = json.loads(table_content)
    http = urllib3.PoolManager()


    print(to_circle, from_circle, table_content)


    # rebalance代码
    ## 修改proxy.json实例，增删实例
    site_info = Influxsite.objects.get(site_no = int(site_no), influx_type='proxy')

    with open(INFLUX_PROXY_CONFIG_PATH + site_info.config_file,"r") as f:
        proxy_config = json.load(f)

    new_circle_config = []

    print(table_content)
    for data in table_content:
        if "checkbox" in data and data["checkbox"]==True:
            continue
        new_circle_config.append({
            "name":data["name"],
            "url":data["url"],
            "username":data["username"],
            "password":data["password"],
            "auth_secure": False if data['auth_secure'] == "False" else True
        })

    to_circle_id = 0
    from_circle_id = 0
    for count, circle in enumerate(proxy_config["circles"]):
        if circle["name"] == to_circle:
            circle["backends"] = new_circle_config
            to_circle_id = count
        if circle["name"] == from_circle:
            from_circle_id = count

    ## 重启influx-proxy代理
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

    r =  http.request('POST','http://%s:%s/recovery?from_circle_id=%d&to_circle_id=%d&worker=%s&u=%s&p=%s'%(site_info.ip, str(site_info.port),from_circle_id,to_circle_id,worker_num,site_info.user,site_info.passwd))
    response_state = r.data.decode('utf-8')
    ## 状态查询
    content= {
        "response_state":response_state
    }

    print("恢复命令已经发出！！！")
    return JsonResponse(content,safe=False)


