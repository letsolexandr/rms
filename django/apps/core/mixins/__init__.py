from ..exceptions import ChangeProtectedFieldException, DeleteProtectedFieldException
from django.core.exceptions import PermissionDenied


class CheckProtected:
    # Значення захищених від зміни полів потрібно задати в дочірньому класі
    PROTECTED_FIELDS = None

    @property
    def is_protected(self):
        if hasattr(self, 'protected'):
            return getattr(self, 'protected')
        else:
            return False

    def check_protected(self):
        if not self.pk:
            return
        if not self.PROTECTED_FIELDS:
            return
        if self.is_protected:
            # if hasattr(self, 'editor'):
            #     if self.editor.is_superuser:
            #         return
            old_version = self.__class__.objects.get(pk=self.pk)
            for protected_field in self.PROTECTED_FIELDS:
                if getattr(old_version, protected_field) != getattr(self, protected_field):
                    raise ChangeProtectedFieldException

    def check_delete_protected(self, *args, **kwargs):
        if self.is_protected:
            if hasattr(self, 'editor') and self.editor:
                if self.editor.is_superuser:
                    return
            raise DeleteProtectedFieldException


class RelatedObjects(object):
    # @property
    # def related_objects(self):
    #     """Повертає список повязаних обєктів"""
    #     obj = self
    #     if not hasattr(obj._meta, 'related_objects'):
    #         return []

    #     related_fields = obj._meta.related_objects
    #     related_list = []
    #     for related in related_fields:
    #         field_name = related.get_cache_name()
    #         if field_name and hasattr(obj, field_name):
    #             related_field = getattr(obj, field_name)
    #             if hasattr(related_field, 'all'):
    #                 queryset = related_field.all()
    #                 children = []
    #                 name = None
    #                 for item in queryset:
    #                     name = item._meta.verbose_name_plural
    #                     children.append({'id': item.id, 'name': str(item)})
    #                 if name:
    #                     data = {'name': name, 'id': obj.id,
    #                             'children': children}
    #                     related_list.append(data)
    #             else:
    #                 if related_field.id !=obj.id:
    #                     data = {'name': str(related_field), 'id': related_field.id}
    #                     related_list.append(data)

    #     return related_list

    def get_related_objects_with_count(self):
        show_limit = 5
        """Повертає список повязаних обєктів"""
        obj = self
        if not hasattr(obj._meta, 'related_objects'):
            return []

        related_fields = obj._meta.related_objects
        related_list = []
        total_count = 0
        for related in related_fields:
            field_name = related.get_cache_name()
            if field_name and hasattr(obj, field_name):
                related_field = getattr(obj, field_name)
                if hasattr(related_field, 'all'):
                    queryset = related_field.all()
                    child_count = queryset.count()
                    total_count += child_count
                    related_objects = queryset[:show_limit]
                    children = []
                    name = None
                    inner_counter = 0
                    for item in related_objects:
                        name = item._meta.verbose_name_plural
                        children.append({'id': item.id, 'name': str(item)})
                        inner_counter += 1
                    if inner_counter < child_count:
                        children.append(
                            {'id': "#", 'name': f'+ ще {child_count-show_limit} елементів'})
                    if name:
                        data = {'name': name, 'id': obj.id,
                                'children': children}
                        related_list.append(data)
                # else:
                #     if related_field.id !=obj.id:
                #         data = {'name': str(related_field), 'id': related_field.id}
                #         related_list.append(data)

        return {"related_objects": related_list, "count": total_count, "title": str(obj)}
