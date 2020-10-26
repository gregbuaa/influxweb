from django.shortcuts import redirect

# Create your code here.
# 验证登录状态
def login_required(fun):
    def inner(request,*args,**kwargs):
        if request.session.get('is_login',None):
            return fun(request,*args,**kwargs)
        else:
            return redirect('/login/?next=' + request.get_full_path())
    return inner