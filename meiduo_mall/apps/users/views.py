from django.shortcuts import render
from django.views import View
from apps.users.models import User
from django.http import JsonResponse
import re

class UsernameCountView(View):
    """判断用户名是否重复注册"""

    def get(self, request, username):

        if not re.match('[a-zA-Z0-9_-]{5,20}',username):
            return JsonResponse({'code':200, 'errmsg':'用户名不满足要求'})
        count = User.objects.filter(username=username).count()
        return JsonResponse({'code': 0, 'errmsg': 'OK', 'count': count})

class MobileCountView(View):
    """判断手机号是否重复注册"""

    def get(self, request, mobile):

        if not re.match('1[3456789]\d{9}',username):
            return JsonResponse({'code':200, 'errmsg':'手机号输入有误'})
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
        #all里的元素只要是None，False
        #all返回Flase，否则返回True
        if not all([username, password, password2, mobile, allow]):
            return JsonResponse({'code':400, 'errmsg':'参数不全'})
        # 用户名是否满足规则
        if not re.match('[a-zA-Z0-9_]{5,20}',username):
            return JsonResponse({'code': 400, 'errmsg': '用户名不满足规则'})

        # 4.数据入库
        User.objects.create_user(username=username, password=password, mobile=mobile)

        # 5.返回响应
        return JsonResponse({'code': 0, 'errmsg': 'OK'})

