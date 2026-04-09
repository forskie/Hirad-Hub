from django import template
register = template.Library()

@register.filter(name='dict_get')
def get_item(dictionary, key):
    return dictionary.get(key)