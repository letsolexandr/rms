from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import (
    UserChangeForm, UserCreationForm,
)
from django.utils.translation import gettext, gettext_lazy as _

from django.contrib.auth.models import Permission, Group
from django.contrib.auth.admin import GroupAdmin
from django.contrib.contenttypes.models import ContentType
from .models import CoreUser, CoreOrganization, AuthorisedPerson
from .mixins.admin_mixin import AdminMixin


admin.site.unregister(Group)


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    search_fields = ['name', 'codename', 'content_type']
    list_display = ["name", "codename", 'content_type']


@admin.register(Group)
class GroupAdmin(GroupAdmin):
    list_display = ["name"]


@admin.register(ContentType)
class ContentTypeAdmin(admin.ModelAdmin):
    search_fields = ['app_label', 'model']
    list_display = ["app_label", "model"]


class ExtendedUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = CoreUser


class ExtendedUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CoreUser


@admin.register(CoreUser)
class ExtendUserAdmin(UserAdmin):
    form = ExtendedUserChangeForm
    add_form = ExtendedUserCreationForm
    autocomplete_fields = ['organization']
    list_display = ('username', 'first_name', 'last_name',
                    'organization', 'is_active')
    list_filter =['is_staff', 'is_superuser', 'is_active', 'groups','organization']
    fieldsets = (
        (None, {'fields': ('username', 'ipn','password', 'organization','auth_type')}),
        (_('Personal info'), {
         'fields': ('first_name', 'last_name', 'email', )}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ( 'ipn', 'username', 'first_name', 'last_name',
            'password1', 'password2','organization','auth_type','groups'),
        }),
    )

from django.forms import ModelForm, Form

class OrganizationForm(ModelForm):
    class Meta:
        model = CoreOrganization
        fields = ['edrpou','name', 'full_name','address','phone','email']


class AuthorisedPersonInLine(admin.TabularInline):
    model = AuthorisedPerson
    extra = 0
    min_num = 0
    max_num = 25


@admin.register(CoreOrganization)
class CoreOrganizationAdmin(AdminMixin, admin.ModelAdmin):
    form = OrganizationForm
    search_fields = ['name', 'edrpou', 'full_name']
    exclude = ['organization', 'region', 'district',
               'settlement', 'street', 'street_type']

    def has_change_permission(self,  request, obj=None) -> bool:
        if request.user.organization == obj:
            return True
        return super().has_change_permission(request, obj)

    def has_view_permission(self, request, obj=None) -> bool:
        if request.user.organization == obj:
            return True
        return super().has_view_permission(request, obj)
    
    inlines = [
        AuthorisedPersonInLine
    ]
