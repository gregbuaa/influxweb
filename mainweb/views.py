from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from .models import Influxsite,Domaininfo,Siteinfo,Tableinfo
from django.db import connection
from influxdb import InfluxDBClient

# Create your views here.
def load_tables_info(request):
    cursor = connection.cursor()
    site_sql = "select `site_no`,`site_name`,`site_chinese_name`,`ip`,`port`,`database`,`database_chinese_name` from `influxsite` order by `site_name`"
    cursor.execute(site_sql)
    site_tables = []
    database_dict = {}
    for row in cursor.fetchall():
        if str(row[0]) not in database_dict:
            database_dict[row[0]] = []
            site_tables.append(
                {
                    "site_no":str(row[0]),
                    "site_name":row[1],
                    "site_chinese_name":row[2],
                    "ip": row[3],
                    "port":str(row[4])
                }
            )
        database_dict[str(row[0])].append({"database":row[5],'database_chinese_name':row[6]})


    for site_info in site_tables:
        site_info['database_list'] = database_dict[site_info['site_no']]

    config_sql = "select `table_name`,`table_chinese_name`,`type` from `tableinfo`"
    cursor.execute(config_sql)
    config_tables = []
    influx_tables = []
    for row in cursor.fetchall():
        temp_con = {
                    "table_name":row[0],
                    "table_chinese_name":row[1]
                }
        if row[2] == 0:
            config_tables.append(temp_con)
        else:
            influx_tables.append(temp_con)

    contents = {
        "config_tables":config_tables,
        "site_tables":site_tables,
        "influx_tables":influx_tables
    }

    return JsonResponse(contents)


def load_site_table(request):
    site_no = request.POST.get('site_no', '1')
    database = request.POST.get('database', 'iot')
    table = request.POST.get('table','telemetry')
    # site_port = request.POST.get()
    site_info = Influxsite.objects.get(site_no=site_no,database=database)
    
    client = InfluxDBClient(host=site_info.ip,port=site_info.port,username=site_info.user,password=site_info.passwd,database=site_info.database)
    
    result = client.query('select * from %s'%(table))

    # print("Result: {0}".format(result))
    test_points = list(result.get_points(measurement=table))
    # print(test_points)

    return JsonResponse(test_points,safe=False)

def to_dict(obj):
    return dict([(attr, getattr(obj, attr)) for attr in [f.name for f in obj._meta.fields]])

def load_config_table(request):
    table_name = request.POST.get('table','domaininfo')
    jsons = []
    # cursor = connection.cursor()
    # site_sql = "select `site_no`,`site_name`,`site_chinese_name`,`ip`,`port`,`database`,`database_chinese_name` from `influxsite` order by `site_name`"
    # cursor.execute(site_sql)
    # contents = []
    # table_trans = {'domaininfo':Domaininfo}
    print(Domaininfo.objects.all().values())






    # for obj in Domaininfo.objects().all():
    #     jsons.append(to_dict(obj)) 
    
    return JsonResponse(jsons,safe=False)





