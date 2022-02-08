from django.http import JsonResponse

from apps.goods.models import SKU
from haystack import indexes

"""
1.需要在模型对应的子应用中创建search_indexes.py
2.索引类必须继承自index.SearchIndex, indexes.Indexable
3.必须定义一个字段 document=True
    所有索引的这一字段必须一直
4.use_template=Ture
    允许单独设置一个文件来指定哪些字段需要检索
    模板文件夹下/search/index/子应用目录/模型类名小写_text.txt
    
    运作：让haystack 将数据获取 给es 来生成索引
    在虚拟环境下 python manage.py rebuild_index 
"""


class SKUIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)

    def get_model(self):
        return SKU

    def index_queryset(self, using=None):
        return self.get_model().objects.all()
        # return SKU.objects.all()



