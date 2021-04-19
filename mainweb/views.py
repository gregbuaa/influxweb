from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from .models import Influxsite,Domaininfo,Siteinfo,Tableinfo,Deviceinfo
from django.db import connection
from influxdb import InfluxDBClient
from django.core import serializers
from copy import deepcopy
import json

import datetime

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
    site_info = Influxsite.objects.get(site_no=site_no,database=database)
    
    client = InfluxDBClient(host=site_info.ip,port=site_info.port,username=site_info.user,password=site_info.passwd,database=site_info.database)
    print("influx sql", 'select * from %s %s order by time desc LIMIT 100'%(table, condition_sql))

    result = client.query('select * from %s %s order by time desc LIMIT 100'%(table, condition_sql)) ## 需要加上时间限制，否则读取的数据过多，导致卡死。

   
    # print("Result: {0}".format(result))
    test_points = list(result.get_points(measurement=table))
    # print(test_points)
    chinese_title = list(Domaininfo.objects.filter(table_name=table).values())
    test_points = [dict([(x,str(y))for x, y in l.items()])for l in test_points]

    cursor = connection.cursor()

    optional_content = {}
    joint_optional_content = {}

    optional_result = Domaininfo.objects.filter(table_name=table,isoptional__gte=1) 
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
        'joint_optional_content':joint_optional_content
    }

    return JsonResponse(content,safe=False)



# def load_site_table1(request):
#     site_no = request.GET.get('site_no', '1')
#     database = request.GET.get('database', 'iot')
#     table = request.GET.get('table_name','telemetry')
#     table_chinese_name = request.GET.get('table_chinese_name','')
#     # site_port = request.POST.get()
#     # print(database,table,site_no)
#     content = {}
#     site_info = Influxsite.objects.get(site_no=site_no,database=database)
    
#     client = InfluxDBClient(host=site_info.ip,port=site_info.port,username=site_info.user,password=site_info.passwd,database=site_info.database)
    
#     result = client.query('select * from %s'%(table)) ## 需要加上时间限制，否则读取的数据过多，导致卡死。

#     # print("Result: {0}".format(result))
#     test_points = list(result.get_points(measurement=table))
#     # print(test_points)
#     chinese_title = list(Domaininfo.objects.filter(table_name=table).values())
#     test_points = [dict([(x,str(y))for x, y in l.items()])for l in test_points]

#     optional_result = Domaininfo.objects.filter(table_name=table,isoptional=1)

#     cursor = connection.cursor()

#     para_list = {}

#     require_translate = {}

#     for result in optional_result:
#         if result.optional == "None":
#             continue
        
#         eles = result.optional.split('|')
#         index = eles[0]
#         # trans_table = eles[1]
#         # trans_domain = eles[2]
#         # trans_domain_chinese = eles[3]

#         if index not in para_list:
#             para_list[index] = []
#             require_translate[index] = ""
        
#         require_translate[index] += (result.domain_name+"|")

#         for i in range(1,len(eles)):
#             para_list[index].append(eles[i])


#     require_translate = list(require_translate.values())

#     # print("require_translate",require_translate)

#     query_sqls = []
#     for table_name, para in para_list.items():
#         query_sql = "select "
#         for p in para:
#             query_sql += (p +  ",")
#             # query_sql +=
#         query_sql = query_sql[0:-1]
#         query_sql += " from "+table_name
#         query_sqls.append(query_sql)

#     print("**********************query_sqls",query_sqls)

#     translate_table = {}
#     for sql in query_sqls:
#         cursor.execute(sql)

#         for row in cursor.fetchall():
#             eng_domain_name = ""
#             eng_domain_chinese_name = ""
#             for i in range(len(row)):
#                 if i % 2 ==0:
#                     eng_domain_name += (row[i]+"|") 
#                 else:
#                     eng_domain_chinese_name += (row[i]+"|")

                
#             translate_table[eng_domain_name] = eng_domain_chinese_name

#         # print("translate_table",translate_table)


#     for points in test_points:
#         for domain in require_translate:
#             # domain_chinese = translate_table(domain)
#             domain_list = domain.split('|')
#             # domain_chinese_list = domain_chinese.split('|')
#             translate_table_index = ""
#             for i in range(len(domain_list) - 1):
#                 translate_table_index += ((points[domain_list[i]]) + "|")

#             if translate_table_index in translate_table:
#                 domain_chinese_list = translate_table[translate_table_index].split('|')
#                 # domain_chinese_list = domain_chinese.split('|')

#                 for i  in range(len(domain_list) - 1):
#                     points[domain_list[i]] = domain_chinese_list[i]

#                 # if domain_list[i] in points:
#                     # points[domain_list[i]] = domain_chinese_list[i]
                
#     content = {
#         "table_name":site_info.site_chinese_name+"-"+site_info.database_chinese_name+"-"+table_chinese_name,
#         "chinese_title":chinese_title,
#         "table_data":test_points
#     }

#     return JsonResponse(content,safe=False)


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



def save_influx_tables(request):
    site_no = request.POST.get('site_no', '1')
    database = request.POST.get('database', 'iot')
    table_name = request.POST.get('table_name','telemetry')
    modify_rows = request.POST.get('modify_row','')

    print("current modify rows ",modify_rows)

    site_info = Influxsite.objects.get(site_no=site_no,database=database)
    
    client = InfluxDBClient(host=site_info.ip,port=site_info.port,username=site_info.user,password=site_info.passwd,database=site_info.database)

    table_attrs = Domaininfo.objects.filter(table_name=table_name)
    title_name = {}
    title_name['fields'] = []
    title_name['tags'] = []
    # title_name['time'] 
    # title_name[]

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
        all_update_data = json.loads(modify_rows)
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


    site_info = Influxsite.objects.get(site_no=site_no,database=database)
    client = InfluxDBClient(host=site_info.ip,port=site_info.port,username=site_info.user,password=site_info.passwd,database=site_info.database)
    
    result = client.query('select * from %s where time >= NOW() -%sms and time <= Now() %s order by time desc'%(table_name,refresh_time, condition_sql)) 
    print("Result: {0}".format(result))
    test_points = list(result.get_points(measurement=table_name))
    test_points = [dict([(x,str(y))for x, y in l.items()])for l in test_points]

    content = {
        "update_data": test_points
    }

    return JsonResponse(content,safe=False)





