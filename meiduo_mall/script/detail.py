#!/usr/bin/env python

import sys
sys.path.insert(0, '../')

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "meiduo_mall.settings")

import django
django.setup()

from apps.goods.models import SKU
from utils.goods import get_categories, get_breadcrumb, get_goods_specs


def generic_detail_html(sku):
    # try:
    #     sku = SKU.objects.get(id=sku_id)
    # except SKU.DoesNotExist:
    #     pass
    # 1.分类数据
    categories = get_categories()
    # 2.面包屑
    breadcrumb = get_breadcrumb(sku.category)
    # 3.SKU信息
    # 4.规格信息
    goods_specs = get_goods_specs(sku)
    context = {
        'categories': categories,
        'breadcrumb': breadcrumb,
        'sku': sku,
        'specs': goods_specs

    }

    from django.template import loader
    detail_template = loader.get_template('detail.html')
    detail_html_data = detail_template.render(context)
    import os
    from meiduo_mall import settings
    file_path = os.path.join(os.path.dirname(settings.BASE_DIR), 'front_end_pc/goods/%s.html' % sku.id)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(detail_html_data)

    print(sku.id)


skus = SKU.objects.all()
for sku in skus:
    generic_detail_html(sku)
