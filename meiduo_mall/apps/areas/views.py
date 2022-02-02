from django.core.cache import cache
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
        # 先查询缓存数据
        province_list = cache.get('province')
        # 如果没有缓存，则查询数据库，并缓存
        if province_list is None:
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

            # 保存缓存数据
            # cache.set(key, value, expire)
            cache.set('province', province_list, 24 * 3600)

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
        # 获取缓存数据
        data_list = cache.get('city:%s' % id)
        if data_list is None:
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

            # 缓存数据
            cache.set('city:%s' % id, data_list, 24 * 3600)

        return JsonResponse({'code': 0, 'errmsg': 'ok', 'sub_data': {'subs': data_list}})

# 不经常发生变化的数据 最好缓存到redis，减少数据库查询
