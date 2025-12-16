from django import template
from catalog.models import Category, Tag

register = template.Library()

@register.simple_tag
def get_categories():
    return Category.objects.all()

@register.simple_tag
def get_tags():
    return Tag.objects.all()
