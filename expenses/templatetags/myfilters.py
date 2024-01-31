from django import template

register = template.Library()

@register.filter
def format_hundreds(value):
    # Use string formatting to insert commas every three digits
    return "{:,}".format(value)