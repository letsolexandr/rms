import uuid
from abc import ABC, abstractmethod

from django.db import models
from django.db.models.signals import post_delete
from django.forms.models import model_to_dict
from django.db.models import ProtectedError
from django.db.models.deletion import get_candidate_relations_to_delete
from .mixins import CheckProtected, RelatedObjects


class SoftDeleteManager(models.Manager):
    MODE_CHOISE = ['clear', 'deleted', 'all']

    def __init__(self, *args, **kwargs):
        mode = kwargs.pop('mode', 'clear')
        ##raise Exception(mode)
        if not mode:
            raise Exception('"mode" is required in "SoftDeleteManager"')

        if mode not in SoftDeleteManager.MODE_CHOISE:
            raise Exception(
                '"mode" must bee in  "SoftDeleteManager.MODE_CHOISE"')
        super(SoftDeleteManager, self).__init__(*args, **kwargs)
        self.mode = mode

    def get_queryset(self):
        base_qeeryset = super(SoftDeleteManager, self).get_queryset()
        ##base_qeeryset = SafeDeleteQueryset(self.model, using=self._db)

        if self.mode == 'clear':
            qs = base_qeeryset.filter(is_deleted=False)
        elif self.mode == 'deleted':
            qs = base_qeeryset.filter(is_deleted=True)
        elif self.mode == 'all':
            qs = base_qeeryset.all()
        else:
            raise Exception('"mode" is not set')

        return qs


class AbstractBase(CheckProtected, RelatedObjects, models.Model):
    DELETE_MODE_VALUES = ['hard', 'soft']
    DEFAULT_DELETE_VALUE = 'soft'
    is_deleted = models.BooleanField(null=False, default=False, editable=False, db_index=True,
                                     verbose_name="**Дані помічено на видалення?")
    unique_uuid = models.UUIDField(default=uuid.uuid4, db_index=True,editable=False,
                                   verbose_name="**Унікальний ідентифікатор запису, в загальному просторі імен",
                                   help_text="Інформацію, відмічену за допомогою UUID, можна використовувати без необхідності вирішення конфлікту імен")
    objects = SoftDeleteManager(mode='clear')
    deleted_objects = SoftDeleteManager(mode='deleted')
    objects_with_deleted = SoftDeleteManager(mode='all')

    class Meta:
        abstract = True

    def check_related_objects(self):
        """ """

        for related in get_candidate_relations_to_delete(self._meta):

            field_name = related.get_cache_name()
            if not field_name:
                return
            if hasattr(self, field_name):
                related_field = getattr(self, field_name)
                if hasattr(related_field, 'exists'):
                    exists = related_field.exists()
                    field = related.field
                    if exists and field.remote_field.on_delete != models.CASCADE:
                        return True
        return False

    def check_if_can_delete(self):
        if self.check_related_objects():
            # TODO можливо виводити перелік обєктів що посилаються
            # ProtectedError(message,related_list)
            raise ProtectedError(None, None)

    def delete(self, **kwargs):
        self.check_if_can_delete()

        mode = kwargs.pop('mode',  self.DEFAULT_DELETE_VALUE)

        if not mode:
            mode = self.DEFAULT_DELETE_VALUE
        if mode not in self.DELETE_MODE_VALUES:
            raise Exception('"mode" in "{}"'.format(
                ','.join(self.DELETE_MODE_VALUES)))
        # Не видаляти повзані обєкти
        # self.delete_related_objects(mode=mode)
        if mode == 'soft':
            self.soft_delete()
        else:
            self.hard_delete()

    def hard_delete(self):
        super(AbstractBase, self).delete()

    def soft_delete(self):
        self._meta.model.objects.filter(pk=self.pk).update(is_deleted=True)
        post_delete.send(sender=self._meta.model,
                         instance=self, using=self._state.db)
        print(self._meta.model)

    def restore(self):
        self.is_deleted = False
        self.save()

    def delete_related_objects(self, mode=None):
        """ Видаляє поваязані обєкти  з каскадним видаленням"""
        obj = self
        for related in get_candidate_relations_to_delete(obj._meta):
            field_name = related.get_cache_name()
            if not field_name:
                return
            if hasattr(obj, field_name):
                related_field = getattr(obj, field_name)
                field = related.field
                if hasattr(related_field, 'all') and field.remote_field.on_delete != models.CASCADE:
                    queryset = related_field.all()
                    for item in queryset:
                        item.editor = self.editor
                        item.delete(mode=mode)
                else:
                    related_field.delete(mode=mode)

    def as_dict(self, fields):
        return model_to_dict(self, fields=fields or [field.name for field in self._meta.fields])

    @property
    def natural_key(self):
        return {'id': self.id, 'value': self.__str__()}


class AbstractService(ABC):
    @abstractmethod
    def run(self):
        pass

    def check_permissions(self):
        # TODO подати обовязкову реалізацію перевірки прав доступу для запуску
        pass