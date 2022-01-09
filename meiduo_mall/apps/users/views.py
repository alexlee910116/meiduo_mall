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
