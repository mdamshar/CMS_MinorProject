from django import template

register = template.Library()

@register.filter
def pluck(queryset, attr):
    """Usage: queryset|pluck:'field' returns a list of field values from a queryset."""
    return [getattr(obj, attr, None) for obj in queryset]

@register.filter(name='has_group')
def has_group(user, group_name):
    return user.groups.filter(name=group_name).exists()
