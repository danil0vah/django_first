from django.db.models import Count
from django import template
from tours.models import *

register = template.Library()

@register.simple_tag(name = 'getcats')
def get_categories(filter = None):
    if not filter:
        return Categories.objects.all()
    else:
        return Categories.objects.filter(pk = filter)

@register.inclusion_tag('tours/list_categories.html')
def show_categories(cats, cat_selected = 0):


    return {'cats': cats, 'cat_selected': cat_selected}

@register.inclusion_tag('tours/list_menu.html')
def show_menu(menu, user):
    
    return {'menu': menu , 'user': user}