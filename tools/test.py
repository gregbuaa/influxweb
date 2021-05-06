from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime
from influxdb import InfluxDBClient
import random



client = InfluxDBClient(host="127.0.0.1",port=7920,username="root",password="root@buaa",database="newiot")
table_name = "telemetry"
result_telem = client.query("select * from telemetry where site_name='西安' order by time desc LIMIT 5")
result_telem = list(result_telem.get_points(measurement=table_name))
print(result_telem)



