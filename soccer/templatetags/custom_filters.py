from django import template

register = template.Library()


@register.filter
def get_standing_color(standing, total):
    if standing == 1:
        return 'text-warning'
    if standing <= 4:
        return 'text-info'
    if standing > total - 3:
        return 'text-danger'
    return ''
