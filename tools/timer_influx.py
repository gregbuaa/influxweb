from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime
from influxdb import InfluxDBClient
import random

client = InfluxDBClient(host="219.224.169.20",port=13005,username="root",password="g927@buaa",database="iot")
table_name = "telesignalling"


def job():
    print("执行一次")
   
    body=  {
            "measurement":table_name,
            "fields": {
                "state":0.0,
                "blocked":0.0,
                'detected_value':round(random.uniform(10,100),1)
            },
            "tags":{
                "site_name":"Shanghai",
                "device_name":"EDFA_relay_device1",
                "data_name":"output_power"
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