from django.shortcuts import redirect
import jwt
import datetime
from jwt import exceptions
import base64

from influxweb.settings import JWT_SALT

# Create your code here.
# 验证登录状态
def login_required(fun):
    def inner(request,*args,**kwargs):
        request.session['is_login'] = True
        request.session['user_id'] = 1
        request.session['user_type'] = "root" # or root or user.
        request.session['user_name'] = "zxy"
        return fun(request,*args,**kwargs)
        # if request.session.get('is_login',None):
        #     return fun(request,*args,**kwargs)
        # else:
        #     return redirect('/login/?next=' + request.get_full_path())
    return inner



def parse_payload(token):
    """
    对token进行和发行校验并获取payload
    :param token:
    :return: {'status': True, 'data': {'iss': 'zhaoxinyu$root'}, 'error': None}
    """
    SALT = JWT_SALT
    SALT = base64.b64decode(JWT_SALT)
    result = {'status': False, 'data': None, 'error': None}
    try:
        verified_payload = jwt.decode(token, SALT,  algorithms=['HS256'])
        result['status'] = True
        result['data'] = verified_payload
    except exceptions.ExpiredSignatureError:
        result['error'] = 'token已失效'
    except jwt.DecodeError:
        result['error'] = 'token认证失败'
    except jwt.InvalidTokenError:
        result['error'] = '非法的token'
    return result

def auth_user(token,request):
    user_name, user_type, error = "", "", "没有token"
    if token == "":
        status = False
    else:
        user_data = parse_payload(token)
        status = user_data['status']
        error = user_data['error']
        if status == True:
            user_name, user_type = user_data['data']['iss'].split('$')
            request.session['is_login'] = True
            request.session['user_id'] = 1
            request.session['user_type'] = user_type # or root or user.
            request.session['user_name'] = user_name

    if status == False:
        request.session['is_login'] = False
        request.session['error'] = error


    request.session['token'] = token

    return request
