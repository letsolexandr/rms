class AdminMixin:
    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.author = request.user
        else:
            obj.editor = request.user
        super().save_model(request, obj, form, change)

    def save_formset(self, request, form, formset, change):
        for f in formset.forms:
            obj = f.instance
            if not obj.author:
                obj.author = request.user
            obj.save()
        formset.save()



# coding: utf-8
from collections import OrderedDict
from functools import partial

from django.contrib import admin
from django.contrib.admin.utils import flatten_fieldsets
from django.contrib.admin.widgets import ForeignKeyRawIdWidget
from django.core.exceptions import ObjectDoesNotExist, FieldError
from django.db.models import ManyToOneRel
from django.forms.models import (modelform_factory, modelform_defines_fields)
from django import forms



class GenericAdminMixin(object):
    def get_form(self, request, obj=None, **kwargs):
        if 'fields' in kwargs:
            fields = kwargs.pop('fields')
        else:
            fields = flatten_fieldsets(self.get_fieldsets(request, obj))

        excluded = self.get_exclude(request, obj)
        exclude = [] if excluded is None else list(excluded)
        readonly_fields = self.get_readonly_fields(request, obj)
        exclude.extend(readonly_fields)
        if excluded is None and hasattr(self.form, '_meta') and self.form._meta.exclude:
            # Take the custom ModelForm's Meta.exclude into account only if the
            # ModelAdmin doesn't define its own.
            exclude.extend(self.form._meta.exclude)
        # if exclude is an empty list we pass None to be consistent with the
        # default on modelform_factory
        exclude = exclude or None

        new_attrs = OrderedDict(
            (f, None) for f in readonly_fields
            if f in self.form.declared_fields
        )
        form = type(self.form.__name__, (self.form,), new_attrs)

        try:
            model = obj.content_type.model_class()
            model_key = model._meta.pk.name
        except (AttributeError, ObjectDoesNotExist):
            model = self.model.content_type.field.formfield().choices.queryset[0].model_class()
            model_key = 'id'

        defaults = {
            "form": form,
            "fields": fields,
            "exclude": exclude,
            "formfield_callback": partial(self.formfield_for_dbfield, request=request),
            "widgets": {
                'object_id': ForeignKeyRawIdWidget(
                    rel=ManyToOneRel(model_key, model, 'id'),
                    admin_site=admin.site
                )
            }
        }
        # defaults.update(kwargs)
        if defaults['fields'] is None and not modelform_defines_fields(defaults['form']):
            defaults['fields'] = forms.ALL_FIELDS

        try:
            return modelform_factory(self.model, **defaults)
        except FieldError as e:
            raise FieldError(
                '%s. Check fields/fieldsets/exclude attributes of class %s.'
                % (e, self.__class__.__name__)
            )