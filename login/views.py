from django.shortcuts import render,redirect
from .models import User
from .forms import UserForm


def hello(request):
    return render(request,'test.html')

def login(request):
    # 不允许重复登录
    if request.session.get('is_login',None):
        return redirect('/')

    if request.method == "POST":
        login_form = UserForm(request.POST)
        message = "请检查填写的内容！"
        next_url = request.GET.get("next", "/")
        if login_form.is_valid():
            username = login_form.cleaned_data['username']
            password = login_form.cleaned_data['password']
            try:
                user = User.objects.get(name=username)
                # print(user.passwd)
                if user.password == password:
                    
                    request.session['is_login'] = True
                    request.session['user_id'] = user.id
                    request.session['user_name'] = user.name
                    return redirect(next_url)
                else:
                    message = "密码不正确！"
            except:
                message = "用户不存在！"
            request.session['message'] = message
            print(message)
        return render(request, 'login/login.html', locals())

    login_form = UserForm()
    return render(request, 'login/login.html', locals())

def logout(request):
    if not request.session.get('is_login', None):
        # 如果本来就未登录，也就没有登出一说
        return redirect("/")
    request.session.flush()
    # 或者使用下面的方法
    # del request.session['is_login']
    # del request.session['user_id']
    # del request.session['user_name']
    return redirect("/")