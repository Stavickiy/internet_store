from django import template
from django.db.models import Count

from vitamins.models import Category

register = template.Library()


@register.inclusion_tag('vitamins/list_categories.html')
def show_categories(cat_selected=None):
    cats = Category.objects.annotate(total=Count('vitamins')).filter(total__gt=0)
    return {'cats': cats, 'cat_selected': cat_selected}
