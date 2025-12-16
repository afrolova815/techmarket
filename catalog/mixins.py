from django.utils.text import slugify
from django.http import QueryDict
from .models import Category, Tag

class DataMixin:
    title = ''
    paginate_by = 10

    def get_title(self):
        return getattr(self, 'title', '') or ''

    def get_querystring(self):
        qs = self.request.GET.copy()
        if 'page' in qs:
            del qs['page']
        return qs.urlencode()

    def get_common_context(self):
        return {
            'title': self.get_title(),
            'querystring': self.get_querystring(),
            'all_categories': Category.objects.all(),
            'all_tags': Tag.objects.all(),
        }

    def get_user_context(self, **kwargs):
        context = self.get_common_context()
        context.update(kwargs)
        return context
