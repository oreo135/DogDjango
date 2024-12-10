from django import template

register = template.Library()

@register.filter
def age_in_human_years(age):
    return age * 7  # Пример перевода возраста собаки в "человеческие годы"
