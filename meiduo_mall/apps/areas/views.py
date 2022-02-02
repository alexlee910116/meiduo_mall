from django.http import JsonResponse
from django.shortcuts import render
from django.views import View

"""
获取省份信息

请求      不需要请求参数
业务逻辑    查询省份信息
响应      JSON
路由      areas/
"""
from apps.areas.models import Area


class AreaView(View):

    def get(self, request):
        # 1. 查询省份信息
        provinces = Area.objects.filter(parent=None)
        # 2.查询结果表
        # 将对象转换为字典数据
        province_list = []
        for province in provinces:
            province_list.append({
                'id': province.id,
                'name': province.name
            })
        # 3.返回响应
        return JsonResponse({'code': 0, 'errmsg': 'ok', 'province_list': province_list})


"""
获取市区信息

请求      获取省份id，市id
业务逻辑    根据id查询信息
响应      JSON
路由      areas/id
"""


class SubAreaView(View):

    def get(self, request, id):
        # Area.objects.filter(parent=id)
        # Area.objects.filter(parent_id=id)

        up_level = Area.objects.get(id=id)
        down_level = up_level.subs.all()
        data_list = []
        for item in down_level:
            data_list.append({
                'id': item.id,
                'name': item.name
            })

        return JsonResponse({'code': 0, 'errmsg': 'ok', 'sub_data': {'subs': data_list}})
