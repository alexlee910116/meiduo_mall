from django.shortcuts import render
from django.views import View
from apps.users.models import User
from django.http import JsonResponse
import re


class UsernameCountView(View):
    """判断用户名是否重复注册"""

    def get(self, request, username):
        if not re.match('[a-zA-Z0-9_-]{5,20}', username):
            return JsonResponse({'code': 200, 'errmsg': '用户名不满足要求'})
        count = User.objects.filter(username=username).count()
        return JsonResponse({'code': 0, 'errmsg': 'OK', 'count': count})


class MobileCountView(View):
    """判断手机号是否重复注册"""

    def get(self, request, mobile):
        if not re.match('1[3456789]\d{9}', mobile):
            return JsonResponse({'code': 200, 'errmsg': '手机号输入有误'})
        count = User.objects.filter(mobile=mobile).count()
        return JsonResponse({'code': 0, 'errmsg': 'OK', 'count': count})


import json


class RegisterView(View):
    def post(self, request):

        # 1.接受请求
        body_bytes = request.body
        body_str = body_bytes.decode()
        body_dict = json.loads(body_str)

        # 2.获取数据
        username = body_dict.get('username')
        password = body_dict.get('password')
        password2 = body_dict.get('password2')
        mobile = body_dict.get('mobile')
        allow = body_dict.get('allow')

        # 3.验证数据
        # all里的元素只要是None，False
        # all返回Flase，否则返回True
        if not all([username, password, password2, mobile, allow]):
            return JsonResponse({'code': 400, 'errmsg': '参数不全'})
        # 用户名是否满足规则
        if not re.match('[a-zA-Z0-9_]{5,20}', username):
            return JsonResponse({'code': 400, 'errmsg': '用户名不满足规则'})

        # 4.数据入库
        # 密码加密
        user = User.objects.create_user(username=username, password=password, mobile=mobile)
        # 状态保持
        from django.contrib.auth import login
        login(request, user)

        # 5.返回响应
        return JsonResponse({'code': 0, 'errmsg': 'OK'})


class LoginView(View):
    # 1.接收数据
    def post(self, request):
        data = json.loads(request.body.decode())
        username = data.get('username')
        password = data.get('password')
        remembered = data.get('remembered')
        # 2.验证数据
        if not all([username, password]):
            return JsonResponse({'code': 400, 'errmsg': '参数不全'})
        # 确定根据用户名还是手机号登录
        if re.match('1[3-9]\d{9}', username):
            User.USERNAME_FIELD = 'mobile'
        else:
            User.USERNAME_FIELD = 'username'
        # 3.验证用户名和密码是否正确
        # 方式1：通过模型根据用户名查询

        # 方式2：
        from django.contrib.auth import authenticate
        user = authenticate(username=username, password=password)

        if user is None:
            return JsonResponse({'code': 400, 'errmsg': '账号密码错误'})

        # 4.session
        from django.contrib.auth import login
        login(request, user)

        # 5.是否记住登录
        if remembered:
            # 记住登录 2周或1个月
            request.session.set_expiry(None)
            pass
        else:
            # 不记住登录 浏览器关闭session过期
            request.session.set_expiry(0)

        # 6.返回响应
        response = JsonResponse({'code': 0, 'errmsg': 'ok'})
        # 为了首页显示用户信息
        response.set_cookie('username', username)
        return response


from django.contrib.auth import logout


class LogoutView(View):
    def delete(self, request):
        # 1.删除session信息
        logout(request)
        response = JsonResponse({'code': 0, 'errmsg': 'ok'})
        # 2.删除cookie信息
        response.delete_cookie('username')
        return response


# 用户中心必须为登录用户
# LoginRequiredMixin 未登录用户会返回重定向
from utils.views import LoginRequiredJSONMixin


class InfoView(LoginRequiredJSONMixin, View):
    def get(self, request):
        # request.user 已经登录的用户信息
        info_data = {
            'username': request.user.username,
            'email': request.user.email,
            'mobile': request.user.mobile,
            'email_active': request.user.email_active,
        }
        return JsonResponse({'code': 0, 'errmsg': 'ok', 'info_data': info_data})
