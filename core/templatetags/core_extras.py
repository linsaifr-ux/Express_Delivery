from django import template

register = template.Library()

@register.filter
def is_active(language_code, current_language_code):
    return language_code == current_language_code
