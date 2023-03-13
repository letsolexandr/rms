# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import random
from django.utils.crypto import get_random_string
import os
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import FileExtensionValidator
from django.db import transaction
from django.utils.translation import gettext_lazy as _

from .abstract_base import AbstractBase
from .exceptions import AuthorNotSet, AuthorOrganizationNotSet
from .mixins import RelatedObjects, CheckProtected
from .settings import USER_COLORS



def default_edrpou():
    return get_random_string(length=8)


class AbstractCoreOrganization(AbstractBase):
    name = models.CharField(blank=True, null=True,max_length=256,
                            db_index=True, verbose_name="Назва")
    full_name = models.CharField(db_index=True,max_length=256,
                                 blank=True, null=True, verbose_name="Повна назва")

    address = models.CharField(db_index=True,
                               max_length=200, blank=True, null=True, verbose_name="Адреса")
    edrpou = models.CharField(max_length=50, blank=True, null=True, db_index=True, verbose_name="ЄДРПОУ",
                              default=default_edrpou)
    phone = models.CharField(max_length=200, blank=True,
                             null=True, verbose_name="Телефон")
    email = models.EmailField(
        max_length=200, blank=True, null=True, verbose_name="EMAIL")
    main_unit = models.CharField(
        max_length=200, blank=True, null=True, verbose_name="Уповноважена особа")
    main_unit_state = models.CharField(
        max_length=200, blank=True, null=True, verbose_name="Посада уповноваженої особи")
    note = models.TextField(blank=True, null=True, verbose_name="Примітка")

    class Meta:
        abstract = True



def get_upload_org_photo_path(instance, filename):
    return os.path.join(
        f'uploads/org_{instance.unique_uuid}/logo/', filename)


CHANGE_ORG_PROFILE_PERMISSION = 'change_org_profile'


class CoreOrganization(AbstractCoreOrganization):
    author = models.ForeignKey('core.CoreUser', related_name='%(class)s_author', null=True, editable=False,
                               on_delete=models.PROTECT, verbose_name="**Автор")
    editor = models.ForeignKey('core.CoreUser', related_name='%(class)s_editor', null=True, editable=False,
                               on_delete=models.PROTECT, verbose_name="**Останній редактор")
    j_index = models.SmallIntegerField(null=False, default=2,
                                       verbose_name="Індекс для використання в журналах реєстрації")
    logo_img = models.FileField(
        upload_to=get_upload_org_photo_path, null=True, verbose_name="Логотип організації",blank=True)

    class Meta:
        verbose_name = 'Центр комплектування та соціальної підтримки'
        verbose_name_plural = 'Центри комплектування та соціальної підтримки'
        unique_together = [ 'edrpou']

        permissions = [
            ('add_simple_organization', "Може створити локальну організацію"),
            ('change_simple_organization', "Може змінити локальну організацію"),
            ('delete_simple_organization', "Може видалити локальну організацію"),
            ('add_local_user', "Може створити локального користувача"),
            ('change_local_user', "Може змінити локального користувача"),
            ('delete_local_user', "Може видалити локального користувача"),
            (CHANGE_ORG_PROFILE_PERMISSION, "Може змінювати профіль організації"),
            ('change_local_user_password',
             "Може змінювати пароль  локального користувача"),
        ]

    def __str__(self):
        return self.__unicode__()


    @property
    def repr_name(self):
        return f'{self.full_name or self.name}'

    def __unicode__(self):
        return f'{self.name or self.full_name} {self.edrpou}'

    def save(self, *args, **kwargs):
        super(CoreOrganization, self).save(*args, **kwargs)



class SystemFieldsMixin(models.Model):
    date_add = models.DateTimeField(auto_now_add=True, null=True, editable=False, verbose_name="**Дата створення",
                                    db_index=True)
    date_edit = models.DateTimeField(auto_now=True, null=True, editable=False, verbose_name="**Дата останньої зміни",
                                     db_index=True)

    class Meta:
        abstract = True


class PersonIdentityMixin(models.Model):
    author = models.ForeignKey('core.CoreUser', related_name='%(class)s_author', null=True, editable=False,
                               on_delete=models.PROTECT, verbose_name="**Автор")
    editor = models.ForeignKey('core.CoreUser', related_name='%(class)s_editor', null=True, editable=False,
                               on_delete=models.PROTECT, verbose_name="**Останій редактор")
    author_display_name = models.TextField(
        null=True, editable=False, verbose_name="**Автор")
    editor_display_name = models.TextField(
        null=True, editable=False, verbose_name="**Останій редактор(відображення)")

    class Meta:
        abstract = True




class ComplexBaseMixin(SystemFieldsMixin, PersonIdentityMixin):
    class Meta:
        abstract = True


class CoreBase(AbstractBase, SystemFieldsMixin, PersonIdentityMixin):
    pass

    def save(self, *args, **kwargs):
        self.check_protected()
        self.set_author_display_name()
        self.set_editor_display_name()
        super(CoreBase, self).save(*args, **kwargs)

    def set_author_display_name(self):
        if not hasattr(self, 'author'):
            return
        # повну назву автора вказуємо лише один раз
        if self.author_display_name:
            return
        if self.author:
            self.author_display_name = self.author.display_name

    def set_editor_display_name(self):
        if not hasattr(self, 'editor'):
            return
        if self.editor:
            self.editor_display_name = self.editor.display_name

    def delete(self, **kwargs):
        self.check_delete_protected()
        super(CoreBase, self).delete(**kwargs)

    class Meta:
        abstract = True


class Department(CoreBase, RelatedObjects):
    DEPARTMENT_TYPE_CHOICES = [
        [1, 'Управління'],
        [2, 'Служба'],
        [3, 'Департамент'],
        [4, 'Відділ'],
        [5, 'Сектор']
    ]
    code = models.CharField(max_length=10, blank=True,
                            null=True, verbose_name='Код')
    name = models.CharField(max_length=200, blank=True,
                            null=True, verbose_name='Назва')
    department_type = models.IntegerField(blank=True, null=True,
                                          verbose_name='Тип структурного підрозділу', choices=DEPARTMENT_TYPE_CHOICES)
    parent = models.ForeignKey('self', null=True, on_delete=models.PROTECT, verbose_name="Кому підпорядкований",
                               related_name='childs')

    class Meta:
        verbose_name = u'Структурний підрозділ'
        verbose_name_plural = u'Структурні підрозділи'

    def get_child_department_ids(self, include_self=True):
        r = []
        if include_self:
            r.append(self.pk)
        for c in Department.objects.filter(parent=self):
            _r = c.get_child_department_ids(include_self=True)
            if 0 < len(_r):
                r.extend(_r)
        return r

    def __str__(self):
        return f'{self.name or "Не вказано"}'


def get_upload_photo_path(instance, filename):
    return os.path.join(
        f'uploads/org_{instance.organization.id}/user_{instance.id}/', filename)


def get_av_clor():
    return random.choice(USER_COLORS)


#######################################################################################################
class AUTH_TYPE(models.TextChoices):
    ISEI = 'ISEI', 'ІСЕІ'
    PASSWORD = 'PASSWORD', 'Пароль'
    BOTH = 'BOTH', 'Всі  доступні'


class CoreUser(RelatedObjects, CheckProtected, AbstractUser):
    auth_type = models.CharField(max_length=50,default=AUTH_TYPE.ISEI, choices=AUTH_TYPE.choices,
                                verbose_name="Тип аутентифікації")
    organization = models.ForeignKey(
        CoreOrganization, null=True,blank=True, on_delete=models.PROTECT, verbose_name="Організація")
    department = models.ForeignKey(
        Department, null=True, on_delete=models.PROTECT, related_name='users')
    first_name = models.CharField(_('first name'), max_length=30, blank=False)
    last_name = models.CharField(_('last name'), max_length=150, blank=False)
    email = models.EmailField(_('email address'), blank=False)
    ipn = models.CharField(max_length=10, null=True,
                           verbose_name="РНОКПП")
    u_index = models.CharField(max_length=2, null=True,
                               verbose_name="Індекс користувача",
                               help_text="Застосовується при формуванні реєстраціного номера документа")
    state = models.CharField(max_length=250, null=True, verbose_name="Посада")
    short_name = models.CharField(
        max_length=150, null=True, verbose_name="Скорочене відображення")
    department_short_name = models.CharField(
        max_length=250, null=True, verbose_name="Скорочене відображення (+ структурний підрозділ)")
    display_name = models.CharField(
        max_length=250, null=True, verbose_name="Повне відображення")
    phone = models.CharField(max_length=20, null=True,
                             blank=True, verbose_name="Телефон")
    photo = models.FileField(
        upload_to=get_upload_photo_path, null=True, verbose_name="Фото користувача",blank=True)
    cached_permissions = models.JSONField(null=True, editable=False, help_text="""
    Містить кешовані значення дозволів користувача, оновлюється сигналом
    """)

    class Meta:
        verbose_name = u'Користувач'
        verbose_name_plural = u'Користувачі'
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return self.get_short_name

    def save(self, *args, **kwargs):
        self.department_short_name = self.get_department_short_name
        self.short_name = self.get_short_name
        self.display_name = self.get_display_name
        return super().save(*args, **kwargs)

    @property
    def get_department_short_name(self):
        if self.department:
            department_part = " - " + str(self.department)
        else:
            department_part = ""
        username = self.short_name

        return f' {username} {department_part} '

    @property
    def get_short_name(self):
        return f'{self.last_name} {self.first_name}'

    @property
    def get_display_name(self):
        return f'{self.last_name or ""} {self.first_name or ""}, {self.state or ""}, {self.department or ""}'


class Counter(models.Model):
    max_value = models.IntegerField(default=0)
    model = models.CharField(max_length=100)

    @classmethod
    def next_id(cls, model,max_value=0):
        cls.dispatch(model)
        with transaction.atomic():
            counter_obj = cls.objects.select_for_update().filter(model=model).first()

            _max_value = 0
            if max_value >  counter_obj.max_value:
                _max_value = max_value
            else:
                _max_value = counter_obj.max_value
            next_id = _max_value  + 1
            counter_obj.max_value = next_id
            counter_obj.save()
            return next_id

    @classmethod
    def dispatch(cls, model):
        with transaction.atomic():
            if cls.objects.select_for_update().filter(model=model).count() == 0:
                cls.objects.create(model=model)



class AuthorisedPerson(CoreBase):
    organization = models.ForeignKey(
        CoreOrganization, on_delete=models.PROTECT, verbose_name="Організація", related_name="authorized_persons")
    full_name = models.CharField(max_length=255, verbose_name="ПІБ", blank=False, null=False)
    code = models.CharField(max_length=10, verbose_name="РНОКПП", blank=False, null=False)
    active = models.BooleanField(default=True,verbose_name="Активний")

    class Meta:
        verbose_name_plural = 'Уповноважені особи'
        verbose_name = 'Уповнважена особа'
        