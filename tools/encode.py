import jwt
import datetime
from jwt import exceptions
import base64

JWT_SALT = "MzQ3NmNkOTA0MGUyYWFjNjZlM2E3NmRmNDM4YWFjNmQxNzFhYTY1ZDllZjljMjQ0MWNiYzc2N2U3NDgwMTlkMzk0MjhlNTUwODFlMDQyY2I1MWVlOGE5MDM1YjY0ODMwMzFlMThiMDFkMzVmNTc1NmFjNGY1MmQyMWVjMjQ0Mjc="


def create_token(payload, timeout=20):
    """
    :param payload:  例如：{'user_id':1,'username':'wupeiqi'}用户信息
    :param timeout: token的过期时间，默认20分钟
    :return:
        """
    headers = {
            'typ': 'jwt',
            'alg': 'HS256'
    }
    payload['exp'] = datetime.datetime.utcnow() + datetime.timedelta(minutes=timeout)
    result = jwt.encode(payload=payload, key=JWT_SALT, algorithm="HS256", headers=headers).encode('utf-8').decode('utf-8')
    return result


def parse_payload(token):
    """
    对token进行和发行校验并获取payload
    :param token:
    :return:
    """
    SALT = JWT_SALT
    SALT = base64.b64decode(JWT_SALT)
    result = {'status': False, 'data': None, 'error': None}
    # verified_payload = jwt.decode(token, SALT,  algorithms=['HS256'])
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


token = create_token({'user_id':1,'username':'wupeiqi'})
print(token)


token2 = "eyJvcmlnaW4iOiJUaW1lIFNlcnZpY2UiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJfX3RvdXJpc3RfXyR1c2VyIn0.HLh5NvM4woEfljY2EcFKFsQgKcpxd_ooyDsni9GK9tc"
print(token2)
print(parse_payload(token2))

# jwt.decode(token,base64.b64decode(secret),algorithms=['HS256'])


