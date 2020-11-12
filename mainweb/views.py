from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from .models import Influxsite,Domaininfo,Siteinfo,Tableinfo,Deviceinfo
from django.db import connection
from influxdb import InfluxDBClient
from django.core import serializers
from copy import deepcopy
import json

# Create your views here.
def load_home(request):
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


    site_sql = "select `site_no`,`site_name`,`site_chinese_name`,`database`,`database_chinese_name` from `influxsite` order by `site_name`"
    cursor.execute(site_sql)
    site_tables = []
    # database_dict = {}

    current_site_no = -1
    # current_site = {}
    current_db = []
    for row in cursor.fetchall():
        site_no = str(row[0])
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
    table = request.GET.get('table_name','telemetry')
    table_chinese_name = request.GET.get('table_chinese_name','')
    # site_port = request.POST.get()
    # print(database,table,site_no)
    content = {}
    site_info = Influxsite.objects.get(site_no=site_no,database=database)
    
    client = InfluxDBClient(host=site_info.ip,port=site_info.port,username=site_info.user,password=site_info.passwd,database=site_info.database)
    
    result = client.query('select * from %s'%(table)) ## 需要加上时间限制，否则读取的数据过多，导致卡死。

    # print("Result: {0}".format(result))
    test_points = list(result.get_points(measurement=table))
    # print(test_points)
    chinese_title = list(Domaininfo.objects.filter(table_name=table).values())
    test_points = [dict([(x,str(y))for x, y in l.items()])for l in test_points]
    content = {
        "table_name":site_info.site_chinese_name+"-"+site_info.database_chinese_name+"-"+table_chinese_name,
        "chinese_title":chinese_title,
        "table_data":test_points
    }

    return JsonResponse(content,safe=False)


def load_config_table(request):
    table_name = request.GET.get('table','siteinfo')
    table_chinese_name = request.GET.get('table_chinese_name','')
    # print(table_name)
    content = {}
    chinese_title = list(Domaininfo.objects.filter(table_name=table_name).values())

    table_obj = Domaininfo
    if table_name == "domaininfo":
        table_obj = Domaininfo
    elif table_name == "siteinfo":
        table_obj = Siteinfo
    elif table_name == "tableinfo":
        table_obj = Tableinfo
    elif table_name == "deviceinfo":
        table_obj = Deviceinfo

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

    try:

        all_update_data = json.loads(modify_rows)
        print(all_update_data)
        for row in all_update_data:
            print(row['id'])
            if 'id' in row and row['id']!="":
                id_no = int(row['id'])
                del row['id']
                table_obj.objects.filter(id=id_no).update(**row)
            else:
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





