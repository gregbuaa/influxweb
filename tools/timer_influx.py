from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime
from influxdb import InfluxDBClient
import random

client = InfluxDBClient(host="127.0.0.1",port=7921,username="root",password="root@buaa",database="newiot")
table_name = "telesignalling"


def job():
    print("执行一次")
   
    body=  {
            "measurement":table_name,
            "fields": {
                'detected_value':round(random.uniform(10,100),1)
            },
            "tags":{
                "site_name":"上海",
                "device_name":"EDFA设备",
                "data_name":"输入光功率"
            }
        }

    # bodys = []
    number = int(random.uniform(0,5))

    bodys = [body] * number
       
    try:
        res = client.write_points(bodys)
    except Exception  as e:
        print(e)




# def job():
#     print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
# 定义BlockingScheduler
sched = BlockingScheduler()
sched.add_job(job, 'interval', seconds=0.5)
sched.start()