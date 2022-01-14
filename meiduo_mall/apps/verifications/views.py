from django.shortcuts import render
from django.http import HttpResponse, JsonResponse

# Create your views here.


"""
前端
    拼接一个url 然后给img img会发起请求
    
后端
    请求      接收路由中的uuid
    业务逻辑   生成图片验证码和图片二进制 通过redis把图片验证码保存起来
    响应      
    路由      GET image_code/uuid/
    步骤         1：接收路由中的uuid
                2：生成图片验证码和图片二进制
                3:通过redis把图片验证码保存起来
                4：返回图片二进制
"""
from django.views import View


class ImageCodeView(View):
    def get(self, request, uuid):
        # 1：接收路由中的uuid
        # 2：生成图片验证码和图片二进制
        from libs.captcha.captcha import captcha
        # text 图片验证码的内容
        # image 图片二进制
        text, image = captcha.generate_captcha()

        # 3: 通过redis把图片验证码保存起来
        # 3.1 进行Redis连接
        from django_redis import get_redis_connection
        redis_cli = get_redis_connection('code')
        # 3.2 操作指令
        # name,time,value
        redis_cli.setex(uuid, 300, text)
        # 4：返回图片二进制
        # 图片为二进制 不能返回JSON
        # content_type=响应体数据类型
        # content_type的语法形式
        # 图片 image/jpeg image/gif image/png
        return HttpResponse(image, content_type='image/jpeg')


class SmsCodeView(View):

    def get(self, request, mobile):
        # 1. 获取请求参数
        image_code = request.GET.get('image_code')
        uuid = request.GET.get('image_code_id')
        # 2. 验证参数
        if not all([image_code, uuid]):
            return JsonResponse({'code': 400, 'errmsg': '参数不全'})
        # 3. 验证图片验证码
        # 3.1 连接redis
        from django_redis import get_redis_connection
        redis_cli = get_redis_connection('code')
        # 3.2 获取redis数据
        redis_image_code = redis_cli.get(uuid)
        if redis_image_code is None:
            return JsonResponse({'code': 400, 'errmsg': '图片验证码已过期'})
        # 3.3 对比
        if redis_image_code.decode().lower() != image_code.lower():
            return JsonResponse({'code': 400, 'errmsg': '图片验证码错误'})
        # 4. 生成短信验证码
        from random import randint
        sms_code = '%06d' % randint(0, 999999)
        # 5. 保存短信验证码
        redis_cli.setex(mobile, 300, sms_code)
        # 6. 发送短信验证码
        from libs.yuntongxun.sms import CCP
        # CCP().send_template_sms(mobile, [sms_code, 5], 1)
        from celery_tasks.sms.tasks import send_sms_code
        send_sms_code.delay(mobile, sms_code)
        # 7. 返回响应
        return JsonResponse({'code': 0, 'errmsg': 'ok'})

        sms_code_client = request.POST.get('sms_code')
        redis_cli = get_redis_connection('verify_code')
        sms_code_server = redis_conn.get('sms_%s' % mobile)  # sms_code_server是bytes
        # 判断短信验证码是否过期
        if not sms_code_server:
            return http.JsonResponse({'code': 400, 'errmsg': '短信验证码失效'})
        # 对比用户输入的和服务端存储的短信验证码是否一致
        if sms_code != sms_code_server.decode():
            return http.JsonResponse({'code': 400, 'errmsg': '短信验证码有误'})

        # 1.提取、校验send_flag
        send_flag = redis_conn.get('send_flag_%s' % mobile)
        if send_flag:
            return http.JsonResponse({'code': 400, 'errmsg': '发送短信过于频繁'})
        # 2.重新写入send_flag
        # 保存短信验证码
        redis_conn.setex('sms_%s' % mobile, 300, sms_code)
        # 写入send_flag
        redis_conn.setex('send_flag_%s' % mobile, 60, 1)
