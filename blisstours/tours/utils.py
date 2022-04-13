from django.db.models import Count
from django.core.cache import cache
from .models import *

menu = [
    {'title': "О сайте", 'url_name': 'about'},
    {'title': "Добавить публикацию", 'url_name': 'add_page'},
    {'title': "Контакты", 'url_name': 'contacts'},
    ]


class DataMixin:
    paginate_by = 3

    def get_user_context(self, **kwargs):
        context = kwargs
        cats = cache.get('cats')
        if not cats:
            context['cats'] = Categories.objects.annotate(Count('tours'))
            cache.set('cats', cats, 60)

        user_menu = menu.copy()
        if not self.request.user.is_authenticated:
            user_menu.pop(1)

        context['menu'] = user_menu
        if 'cat_selected' not in context:
            context['cat_selected'] = 0
        return context

