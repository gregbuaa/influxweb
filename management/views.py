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

    print(health_state)

    return render(request,'current_state.html',contents)





