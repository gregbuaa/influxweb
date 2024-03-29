from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from .models import Influxsite,Domaininfo,Siteinfo,Tableinfo,Deviceinfo2,Telesignalling,Telemetry,ResourceInfo, ControlInfo
from django.db import connection
from influxdb import InfluxDBClient
from django.core import serializers
from copy import deepcopy
import json
from copy import deepcopy
import datetime
import jwt
import datetime
from jwt import exceptions
import base64
from login.utils import auth_user

from influxweb.settings import JWT_SALT



# Create your views here.
def load_home(request):   
    token= request.GET.get('token', '')
    request = auth_user(token, request)

    return render(request,'index.html')


def load_tables_info(request):
    cursor = connection.cursor()

    config_sql = "select `table_name`,`table_chinese_name`,`type` from `tableinfo`"
    cursor.execute(config_sql)
    config_tables = []
    influx_tables = []
    for row in cursor.fetchall():
        temp_con = {
                    "name":row[0],
                    "chinese_name":row[1]
                }
        if row[2] == 0:
            config_tables.append(temp_con)
        else:
            influx_tables.append(temp_con)


    site_sql = "select `site_no`,`site_name`,`site_chinese_name`,`database`,`database_chinese_name` from `influxsite` order by `site_name` desc" 
    cursor.execute(site_sql)
    site_tables = []
    # database_dict = {}

    current_site_no = -1
    # current_site = {}
    current_db = []
    for row in cursor.fetchall():
        site_no = str(row[0])
        print("site_no",site_no)
        site_name = row[1]
        site_chinese_name = row[2]
        db_name = row[3]
        db_chinese_name = row[4]

        if current_site_no != site_no:
            site_tables.append({
                "site_no":site_no,
                "name":site_name,
                "chinese_name":site_chinese_name
            })
            current_site_no = site_no
            if len(site_tables) > 0:
                site_tables[-1]['children'] = current_db
                current_db = []
            

        if current_site_no == site_no:
            tables = deepcopy(influx_tables)
            for i in range(len(tables)):
                tables[i]['database'] = db_name
                tables[i]['site_no'] = site_no
                tables[i]['chinese_database'] = db_chinese_name
                print(db_name)
            current_db.append({
                "name": db_name,
                "chinese_name":db_chinese_name,
                "children": tables
            })

        site_tables[-1]['children']=current_db

    contents = {
        "config_tables":config_tables,
        "site_tables":site_tables
        # "influx_tables":influx_tables
    }

    return JsonResponse(contents)


def load_site_table(request):
    site_no = request.GET.get('site_no', '1')
    database = request.GET.get('database', 'iot')
    chinese_database = request.GET.get('chinese_database','数据中心')
    table = request.GET.get('table_name','telemetry')
    table_chinese_name = request.GET.get('table_chinese_name','')
    # influx_type = request.GET.get('influx_type', '')

    print("table", database)

    all_keys = request.GET.get('all_keys','')

    all_keys = json.loads(all_keys)

    condition_sql = ""
    for domain_name1, domain_value1 in all_keys.items():
        if 'time' in domain_name1:
            time_value = datetime.datetime.strptime(domain_value1, '%Y-%m-%d %H:%M:%S').isoformat("T")+"Z"
            # print(time_value)
            if domain_name1 == "from_time":
                condition_sql += "time >= '%s' and " %(time_value)
            elif domain_name1 == "to_time":
                condition_sql += "time <= '%s' and " %(time_value)
        else:
            if domain_value1 != "all":
                condition_sql += "%s='%s' and "%(domain_name1, domain_value1)

    if condition_sql !="":
        condition_sql = "where "+condition_sql[0:-4]+" "

    # site_port = request.POST.get()
    # print(database,table,site_no)
    content = {}
    site_info = Influxsite.objects.get(site_no=site_no,database=database,database_chinese_name=chinese_database)

    influx_type = site_info.influx_type

    if  site_info.user == "" and site_info.passwd== "":
        client = InfluxDBClient(host=site_info.ip,port=site_info.port,database=site_info.database)
    else:
        client = InfluxDBClient(host=site_info.ip,port=site_info.port,username=site_info.user,password=site_info.passwd,database=site_info.database)
    print("influx sql", 'select * from %s %s order by time desc LIMIT 100 '%(table, condition_sql))

    result = client.query("select * from %s %s order by time desc LIMIT 100"%(table, condition_sql)) ## 需要加上时间限制，否则读取的数据过多，导致卡死。

   
    # print("Result: {0}".format(result))
    test_points = list(result.get_points(measurement=table))
    # print(test_points)
    chinese_title = list(Domaininfo.objects.filter(table_name=table,table_type="influx").order_by('id').values())
    test_points = [dict([(x,str(y))for x, y in l.items()])for l in test_points]

    cursor = connection.cursor()

    optional_content = {}
    joint_optional_content = {}

    optional_result = Domaininfo.objects.filter(table_name=table,isoptional__gte=1,table_type="influx") 
    for result in optional_result:
        if result.optional == "None":
            continue
        
        result_split = (result.optional).split('|')
        print(result_split)
        if len(result_split) == 3:
            table_name = result_split[0]
            domain_name = result_split[1]
            domain_chinese_name = result_split[2]

            select_sql = "select DISTINCT `%s`,`%s` from `%s`"%(domain_name, domain_chinese_name, table_name)
            cursor.execute(select_sql)

            for row in cursor.fetchall():

                if domain_name not in optional_content:
                    optional_content[domain_name] = []

                optional_content[domain_name].append({"id":row[0],"text":row[1]})
        
        if len(result_split) == 4:
            # print('true')
            table_name = result_split[0]
            domain_name = result_split[1]
            domain_chinese_name = result_split[2]
            joint_domain_name = result_split[3]

            select_sql = "select `%s`, `%s`, `%s` from `%s`" %(domain_name,domain_chinese_name,joint_domain_name,table_name)
            cursor.execute(select_sql)
            for row in cursor.fetchall():
                if row[2] not in joint_optional_content:
                    joint_optional_content[row[2]] = []

                joint_optional_content[row[2]].append({'id':row[0],'text':row[1]})

    # print(joint_optional_content)

    content = {
        "table_name":site_info.site_chinese_name+"-"+site_info.database_chinese_name+"-"+table_chinese_name,
        "chinese_title":chinese_title,
        "table_data":test_points,
        "optional_content":optional_content,
        'joint_optional_content':joint_optional_content,
        'influx_type':influx_type
    }

    return JsonResponse(content,safe=False)


def load_config_table(request):
    table_name = request.GET.get('table','siteinfo')
    table_chinese_name = request.GET.get('table_chinese_name','')
    # print(table_name)
    content = {}
    chinese_title = list(Domaininfo.objects.filter(table_name=table_name,table_type="mysql").values())

    table_obj = Domaininfo
    if table_name == "domaininfo":
        table_obj = Domaininfo
    elif table_name == "siteinfo":
        table_obj = Siteinfo
    elif table_name == "tableinfo":
        table_obj = Tableinfo
    elif table_name == "deviceinfo2":
        table_obj = Deviceinfo2
    elif table_name == "telemetry":
        table_obj = Telemetry
    elif table_name == "telesignalling":
        table_obj = Telesignalling
    elif table_name == "resource_info":
        table_obj = ResourceInfo
    elif table_name == "control_info":
        table_obj = ControlInfo


    data = list(table_obj.objects.values())
    data = [dict([(x,str(y))for x, y in l.items()])for l in data]
    content = {
        "table_name":table_name,
        "table_chinese_name":"MySQL配置数据库"+"-"+table_chinese_name,
        "chinese_title":chinese_title,
        "table_data":data
    }

    return JsonResponse(content,safe=False)

def del_config_tables(request):
    table_name = request.POST.get('table_name','')
    modify_rows = request.POST.get('modify_row','')

    del_state = 0
    del_info = ""
    table_obj = Domaininfo
    
    if table_name == "domaininfo":
        table_obj = Domaininfo
    elif table_name == "siteinfo":
        table_obj = Siteinfo
    elif table_name == "tableinfo":
        table_obj = Tableinfo
    elif table_name == "deviceinfo":
        table_obj = Deviceinfo
    elif table_name == "telemetry":
        table_obj = Telemetry
    elif table_name == "telesignalling":
        table_obj = Telesignalling
    elif table_name == "resource_info":
        table_obj = ResourceInfo
    elif table_name == "control_info":
        table_obj = ControlInfo

    all_update_data = json.loads(modify_rows)
    print(all_update_data)

    try:
        all_update_data = json.loads(modify_rows)
        print(all_update_data)
        table_obj.objects.get(id=all_update_data['id']).delete()
        del_state = 1
        del_info = "删除成功！"
    except Exception  as e:
        print(e)
        del_state = 0
        del_info = "删除失败！请检查数据格式！"

    content = {
        "del_state":del_state,
        "del_info":del_info
    }

    return JsonResponse(content,safe=False)



def save_config_tables(request):
    table_name = request.POST.get('table_name','')
    modify_rows = request.POST.get('modify_row','')
    # print(table_name)
    # print(modify_rows)

    update_state = 0
    update_info = ""

    # table_name = table_name.split('-')[1]
    # print(table_name)
    table_obj = Domaininfo
    
    if table_name == "domaininfo":
        table_obj = Domaininfo
    elif table_name == "siteinfo":
        table_obj = Siteinfo
    elif table_name == "tableinfo":
        table_obj = Tableinfo
    elif table_name == "deviceinfo":
        table_obj = Deviceinfo
    elif table_name == "telemetry":
        table_obj = Telemetry
    elif table_name == "telesignalling":
        table_obj = Telesignalling
    elif table_name == "resource_info":
        table_obj = ResourceInfo
    elif table_name == "control_info":
        table_obj = ControlInfo

    try:
        all_update_data = json.loads(modify_rows)
        updated_data = []
        for elem in all_update_data:
            updated_data.append(deepcopy(elem))
        
        for index, row in enumerate(all_update_data):
            for key,value in row.items():
                if value.lower()=="none" or value == "":
                    del updated_data[index][key]

        print(updated_data)
        for row in updated_data:
            if 'id' in row and row['id']!="":
                id_no = int(row['id'])
                del row['id']
                table_obj.objects.filter(id=id_no).update(**row)
            else:
                if 'id' in row:
                    del row['id']
                table_obj.objects.create(**row)


        update_state = 1
        update_info = "更新成功！"
    except Exception  as e:
        print(e)
        update_state = 0
        update_info = "更新失败！请检查数据格式！"

    content = {
        "update_state":update_state,
        "update_info":update_info
    }

    return JsonResponse(content,safe=False)



def save_influx_in_one_site(site_no, database, table_name, modify_rows, table_attrs,subscribe):
    site_info = Influxsite.objects.get(site_no=site_no,database=database, influx_type='proxy')
    client = InfluxDBClient(host=site_info.ip,port=site_info.port,username=site_info.user,password=site_info.passwd,database=site_info.database)
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

    update_state = 0
    update_info = ""
    try:
        bodys = []
        for data in modify_rows:
            site_name = data['site_name']
            ### 不是订阅的主题，不给予考虑的。
            if site_name not in subscribe:
                continue
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

#### 添加一个全局同布的功能，即修改的数据要同步到所有订阅主题的机器上去。
def save_influx_tables(request):
    site_no = request.POST.get('site_no', '1')
    database = request.POST.get('database', 'iot')
    table_name = request.POST.get('table_name','telemetry')
    modify_rows = request.POST.get('modify_row','')
    table_attrs = Domaininfo.objects.filter(table_name=table_name,table_type="influx")

    all_update_data = json.loads(modify_rows)
    update_state, update_info = True, ""
    all_subjects_sqls = [] 
    for data in all_update_data:
        all_subjects_sqls.append(" `subscribe` like '%"+data['site_name']+"%' ") 

    subjects_sql = " or ".join(all_subjects_sqls)
    select_sql = "select `site_no`, `database`,`subscribe` from `influxsite` where `influx_type`='proxy' and (%s)"%subjects_sql

    cursor = connection.cursor()
    cursor.execute( select_sql)
    need_modify_sites = []
    for row in cursor.fetchall():
        need_modify_sites.append(
            {
                "site_no":row[0],
                "database":row[1],
                "subscribe":row[2]
            }
        )

    for site in need_modify_sites:
        update_state, update_info = save_influx_in_one_site(site['site_no'], site['database'], table_name, all_update_data, table_attrs, site['subscribe'])

    if len(need_modify_sites) == 0:
        update_state, update_info = save_influx_in_one_site(site_no, database, table_name, all_update_data, table_attrs,",".join(all_subjects_sqls))

    content = {
        "update_state":update_state,
        "update_info":update_info
    }

    return JsonResponse(content,safe=False)



def refresh_influx_table(request):
    print('hello world')
    site_no = request.POST.get('site_no', '1')
    database = request.POST.get('database', 'iot')
    table_name = request.POST.get('table_name','telemetry')
    refresh_time = request.POST.get('refresh_time','1000')
    all_keys = request.POST.get('all_keys','')

    all_keys = json.loads(all_keys)
    print('all_keys',all_keys)

    condition_sql = ""
    
    for domain_name1, domain_value1 in all_keys.items():
        # print('domain_name1',domain_name1)
        if 'time' in domain_name1:
            pass
        else:
            if domain_value1 != "all":
                condition_sql += "%s='%s' and "%(domain_name1, domain_value1)


    if condition_sql !="":
        condition_sql = "and "+condition_sql[0:-4]+" "


    site_info = Influxsite.objects.get(site_no=site_no,database=database,influx_type="proxy")
    client = InfluxDBClient(host=site_info.ip,port=site_info.port,username=site_info.user,password=site_info.passwd,database=site_info.database)
    
    result = client.query('select * from %s where time >= NOW()+8h -%sms-800ms and time <= NOW()+8h %s order by time desc'%(table_name,refresh_time, condition_sql)) 
    print("Query Order", 'select * from %s where time >= NOW()+8h-%sms-1s and time <= NOW()+8h %s order by time desc'%(table_name,refresh_time, condition_sql))
    print("Result: {0}".format(result))
    test_points = list(result.get_points(measurement=table_name))
    test_points = [dict([(x,str(y))for x, y in l.items()])for l in test_points]

    content = {
        "update_data": test_points
    }

    return JsonResponse(content,safe=False)





