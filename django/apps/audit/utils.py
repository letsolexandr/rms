from __future__ import unicode_literals

from uuid import UUID
import os

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import NOT_PROVIDED, DateTimeField
from django.db.models import FileField
from django.utils import timezone
from django.utils.encoding import smart_str as smart_text
from apps.audit.settings import IGNORE_FIELDS
MEDIA_ROOT = settings.MEDIA_ROOT
MEDIA_URL = settings.MEDIA_URL

def get_field_value(obj, field):
    """
    Gets the value of a given model instance field.
    :param obj: The model instance.
    :type obj: Model
    :param field: The field you want to find the value of.
    :type field: Any
    :return: The value of the field as a string.
    :rtype: str
    """
    if isinstance(field, DateTimeField):
        # DateTimeFields are timezone-aware, so we need to convert the field
        # to its naive form before we can accuratly compare them for changes.
        try:
            value = field.to_python(getattr(obj, field.name, None))
            if value is not None and settings.USE_TZ and not timezone.is_naive(value):
                value = timezone.make_naive(value, timezone=timezone.utc)
        except ObjectDoesNotExist:
            value = field.default if field.default is not NOT_PROVIDED else None
    else:
        try:
            value = smart_text(getattr(obj, field.name, None))
            if field.choices:
                value = getattr(obj, f'get_{field.name}_display')()
            ## перевіряємо чи файл    
            if isinstance(field,FileField):
                _value =getattr(obj, field.name)
                if _value:
                    name = _value.name
                    value = os.path.join(MEDIA_URL,name)

        except ObjectDoesNotExist:
            value = field.default if field.default is not NOT_PROVIDED else None

    return value


def model_delta(old_model, new_model):
    """
    Provides delta/difference between two models
    :param old: The old state of the model instance.
    :type old: Model
    :param new: The new state of the model instance.
    :type new: Model
    :return: A dictionary with the names of the changed fields as keys and a
             two tuple of the old and new field values
             as value.
    :rtype: dict
    """

    delta = {}
    fields = new_model._meta.fields

    for field in fields:
        if field.name in IGNORE_FIELDS:
            continue
        old_value = get_field_value(old_model, field)
        new_value = get_field_value(new_model, field)
        if old_value != new_value:
            delta[field.name] = {"verbose_name":field.verbose_name.title().lower(),
                                "old_value":smart_text(old_value),
                                 "new_value":smart_text(new_value),
                                 "type":field.__class__.__name__}

    if len(delta) == 0:
        delta = None

    return delta





def get_m2m_field_name(model, instance):
    """
    Finds M2M field name on instance
    Called from m2m_changed signal
    :param model: m2m_changed signal model.
    :type model: Model
    :param instance:m2m_changed signal instance.
    :type new: Model
    :return: ManyToManyField name of instance related to model.
    :rtype: str
    """
    for x in model._meta.related_objects:
        if x.related_model().__class__ == instance.__class__:
            return x.remote_field.name

def get_m2m_field(model, instance):
    """
    Finds M2M field name on instance
    Called from m2m_changed signal
    :param model: m2m_changed signal model.
    :type model: Model
    :param instance:m2m_changed signal instance.
    :type new: Model
    :return: ManyToManyField name of instance related to model.
    :rtype: str
    """
    for x in model._meta.related_objects:
        print( x.related_model().__class__,x.remote_field,instance.__class__)
        if x.related_model().__class__ == instance.__class__:
            return x.remote_field

