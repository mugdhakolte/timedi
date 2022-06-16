import re
from datetime import datetime

from django import template


register = template.Library()


@register.filter
def created_at_format(format_date):
    return str(datetime(*map(int, re.split('[^\d]', format_date)[:-1])).date())
