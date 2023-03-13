import logging
import uuid
from django.template import Context, Library
from django.utils.safestring import mark_safe
from django.apps import apps
from jazzmin.templatetags.jazzmin import get_sections
from django.conf import settings

from django.contrib.admin.views.main import (
    ALL_VAR, ORDER_VAR, PAGE_VAR, SEARCH_VAR,
)
from django.utils.html import format_html
register = Library()
logger = logging.getLogger(__name__)

@register.simple_tag
def settings_value(name):
    return getattr(settings, name, "")


@register.simple_tag
def get_state():
    return uuid.uuid4()


