from django import template
from django.template.defaultfilters import stringfilter

import markdown as md

register = template.Library()


@register.simple_tag(name="returnbgkey")
def returnBgKey(value):
    column_colors = {
        "A": 'bg-success',
        "C": 'bg-warning',
        "X": 'bg-danger',
        "Y": 'bg-primary',
        "Z": 'bg-dark text-white'
    }
    try:
        return column_colors[value]
    except KeyError:
        return column_colors['Y']