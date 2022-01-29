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
        # request.user 来源于中间件
        # 系统会进行判断，如果确实是登录用户，则可以取得 登录用户对应的模型实例数据
        # 如果不是登录用户，request.user = AnoymousUser
        info_data = {
            'username': request.user.username,
            'email': request.user.email,
            'mobile': request.user.mobile,
            'email_active': request.user.email_active,
        }
        return JsonResponse({'code': 0, 'errmsg': 'ok', 'info_data': info_data})


class EmailView(LoginRequiredJSONMixin, View):
    def put(self, request):
        # 1.接受请求
        data = json.loads(request.body.decode())
        # 2.获取数据
        email = data.get('email')
        user = request.user
        # user/request就是登录用户 实例对象
        user.email = email
        user.save()

        from django.core.mail import send_mail
        # subject, message, from_email, recipient_list

        subject = '美多商城激活邮件'
        message = ''
        from_email = '美多商城<alexlee910116@gmail.com>'
        recipient_list = [email]
        # user_id=1
        from apps.users.utils import generic_email_verify_token
        token = generic_email_verify_token(request.user.id)
        verify_url = 'https://www.meiduo.site:8080/success_verify_email.html?token=%s' % token
        html_message = '<p>尊敬的用户您好！</p>' \
                       '<p>感谢您使用美多商城。</p>' \
                       '<p>您的邮箱为：%s 。请点击此链接激活您的邮箱：</p>' \
                       '<p><a href="%s">%s<a></p>' % (email, verify_url, verify_url)

        # send_mail(subject=subject,
        #           message=message,
        #           from_email=from_email,
        #           recipient_list=recipient_list,
        #           html_message=html_message, )
        from celery_tasks.email.tasks import celery_send_email
        celery_send_email.delay(
            subject=subject,
            message=message,
            from_email=from_email,
            recipient_list=recipient_list,
            html_message=html_message
        )

        return JsonResponse({'code': 0, 'errmsg': 'ok'})


class EmailVerifyView(View):
    def put(self, request):
        params = request.GET
        token = params.get('token')
        if token is None:
            return JsonResponse({'code': 400, 'errmsg': '参数丢失'})
        from apps.users.utils import check_verify_token
        user_id = check_verify_token(token)
        if user_id is None:
            return JsonResponse({'code': 400, 'errmsg': '参数错误'})

        user = User.objects.get(id=user_id)
        user.email_active = True
        user.save()
        return JsonResponse({'code': 0, 'errmsg': 'ok'})
