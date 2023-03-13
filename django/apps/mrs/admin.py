from django.contrib import admin
from django.utils.html import format_html
from django.contrib.admin import SimpleListFilter, BooleanFieldListFilter
from apps.core.admin import AdminMixin
from .models import (MilitaryRank, MilitaryPerson, Child, Education, ForeignLanguage, MilitaryMovement,
                     MilitaryRegistrationViolation, MobilizationPostponement, Company, CompanyEmployee,
                     MilitaryPersonPhone, Notice, NoticeDelivery, MobilizationPostponementDoc, MobilizationPostponementOrgDoc,
                     TCKEmployee, MilitarySpecialty, Language,MilitaryTraining,DocStatus
                     )


admin.site.site_header = "Система обліку військовозобов'язаних(демо)"
admin.site.site_title = "СОВ"
admin.site.index_title = "Система обліку військовозобов'язаних(не містить реальних даних, будь-які співпадіння є випадковими)"


class MobilizationPostponementInline(admin.TabularInline):
    model = MobilizationPostponement
    min_num = 0
    extra = 0


class MilitaryRegistrationViolationInline(admin.TabularInline):
    classes = ('grp-collapse grp-closed',)
    model = MilitaryRegistrationViolation
    min_num = 0
    extra = 0


class ChilInline(admin.TabularInline):
    classes = ('grp-collapse grp-closed',)
    model = Child
    min_num = 0
    extra = 0


class EducationInline(admin.TabularInline):
    classes = ('grp-collapse grp-closed',)
    model = Education
    min_num = 0
    extra = 0


class ForeignLanguageInline(admin.TabularInline):
    classes = ('grp-collapse grp-closed',)
    model = ForeignLanguage
    min_num = 0
    extra = 0


class MilitaryMovementInline(admin.TabularInline):
    classes = ('grp-collapse grp-closed',)
    model = MilitaryMovement
    min_num = 0
    extra = 0


class CompanyEmployeeInline(admin.TabularInline):
    model = CompanyEmployee
    autocomplete_fields = ['company',]
    min_num = 0
    extra = 0


@admin.register(TCKEmployee)
class TCKEmployeeAdmin(AdminMixin, admin.ModelAdmin):
    list_display = ['military_person', 'tck', 'hired_date', 'termination_date']
    autocomplete_fields = ['military_person', 'tck']
    list_per_page = 20


class TCKEmployeeInline(admin.TabularInline):
    model = TCKEmployee
    autocomplete_fields = ['tck',]
    min_num = 0
    extra = 0


class MilitaryPersonPhoneInline(admin.TabularInline):
    model = MilitaryPersonPhone
    min_num = 0
    extra = 0


class MilitaryTrainingInline(admin.TabularInline):
    model = MilitaryTraining
    autocomplete_fields = ['military_specialty',]
    min_num = 0
    extra = 0




@admin.register(Company)
class CompanyAdmin(AdminMixin, admin.ModelAdmin):
    list_display = ['name', 'edrpou', 'address']
    list_per_page = 20
    search_fields = ['name', 'edrpou', 'address']


@admin.register(Language)
class LanguageAdmin(AdminMixin, admin.ModelAdmin):
    list_display = ['code', 'name']
    list_per_page = 20
    search_fields = ['code', 'name']


@admin.register(MilitarySpecialty)
class MilitarySpecialtyAdmin(AdminMixin, admin.ModelAdmin):
    list_display = ['code', 'title']
    list_per_page = 20
    search_fields = ['code', 'title']


class NoticeDeliveryInline(admin.TabularInline):
    model = NoticeDelivery
    min_num = 0
    extra = 0


@admin.register(Notice)
class NoticeAdmin(AdminMixin, admin.ModelAdmin):
    list_display = ['date_add', 'military_person', 'company']
    list_per_page = 20
    autocomplete_fields = ['military_person', 'company']
    inlines = [NoticeDeliveryInline]


class NoticeInline(admin.TabularInline):
    classes = ('grp-collapse grp-closed',)
    autocomplete_fields = ['company']
    show_change_link = True
    model = Notice
    min_num = 0
    extra = 0


@admin.register(MilitaryRank)
class MilitaryRankAdmin(AdminMixin, admin.ModelAdmin):
    list_display = ['name',]
    list_per_page = 20
    search_fields = ['name']




@admin.register(MobilizationPostponementDoc)
class MobilizationPostponementDocAdmin(AdminMixin, admin.ModelAdmin):
    list_display = ['reason', 'status', 'start_date', 'expiration_date']
    list_per_page = 20
    readonly_fields=['military_person']
    autocomplete_fields = ['military_person']


    def get_queryset(self, request):
        has_perm = request.user.has_perm('mrs.can_review_postponement_doc')
        if has_perm:
            return super().get_queryset(request) 
        else:
            return super().get_queryset(request).filter(author=request.user) 


    def get_readonly_fields(self,  request, obj=None):
        has_perm = request.user.has_perm('mrs.can_review_postponement_doc')
        if not has_perm:
            if obj and obj.status == DocStatus.DENIED:
                return ['status','reject_reason']
            return ['status']
        
        return super().get_readonly_fields(request, obj)
    
    def has_change_permission(self, request, obj=None):
        has_perm = request.user.has_perm('mrs.can_review_postponement_doc')
        if  has_perm:
            return True
        if obj and obj.status == DocStatus.NEW:
            return True
        else:
            return False
        
    def get_exclude(self, request, obj=None):
        has_perm = request.user.has_perm('mrs.can_review_postponement_doc')
        if not has_perm:
            if not obj or obj.status != DocStatus.DENIED:
                return ['reject_reason','military_person']
            return ['military_person']
        return super().get_exclude(request, obj)


@admin.register(MobilizationPostponementOrgDoc)
class MobilizationPostponementOrgDocAdmin(AdminMixin, admin.ModelAdmin):
    list_display = ['reason', 'start_date', 'expiration_date']
    autocomplete_fields = ['military_person']
    list_per_page = 20

    def get_readonly_fields(self,  request, obj=None):
        has_perm = request.user.has_perm('mrs.can_review_postponement_doc')
        if not has_perm:
            return ['status']
        return super().get_readonly_fields(request, obj)
    



class TCKFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = 'В мене на обліку'
    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'only_my_tck'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        if request.user.organization:
            return (
                ('1', 'На обліку в моєму ТЦК'),
            )

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        # Compare the requested value (either '80s' or '90s')
        # to decide how to filter the queryset.
        if self.value() == '1':
            return queryset.filter(tcks=request.user.organization)


@admin.register(MilitaryPerson)
class MilitaryPersonAdmin(AdminMixin, admin.ModelAdmin):
    list_display = ['passport_series', 'passport_number',
                    'taxpayer_id', 'last_name', 'first_name', 'date_of_birth', 'military_rank', 'military_specialty',
                    'accounting_group', 'blood_group']
    list_filter = ['blood_group', 'military_rank',
                   'accounting_group', 'military_specialty', TCKFilter]
    autocomplete_fields = ['military_specialty',]
    list_per_page = 20
    search_fields = ['taxpayer_id']
    show_full_result_count = False

    def image_tag(self, obj):
        return format_html('<img  style="height: 150px;" src="{}" />'.format(obj.photo.url))

    image_tag.short_description = 'Image'
    readonly_fields = ['image_tag']

    inlines = [ChilInline,TCKEmployeeInline,  MilitaryPersonPhoneInline,  MilitaryTrainingInline,
               CompanyEmployeeInline,  MobilizationPostponementInline,MilitaryMovementInline,EducationInline, ForeignLanguageInline, MilitaryRegistrationViolationInline, NoticeInline,]

    fieldsets = (
        ('Загальна інформація', {
            'fields': ('photo', 'image_tag',
                       ('last_name', 'first_name'),
                       ('middle_name', 'gender'),
                       ('date_of_birth'),
                       'place_of_birth',
                       'residence_address',
                       'current_address')
        }),
        ('Пастпортні дані', {
            'fields': (('passport_series', 'passport_number'),
                       'passport_issue_date',
                       'passport_issuing_authority',
                       'passport_expiration_date',
                       'taxpayer_id'
                       )
        }),
        (' Дані військового обліку', {
            'fields': ('military_rank', 'military_specialty', 'military_education_level',
                       'reserve_category', 'accounting_group', 'disability_group',
                       'health_status', 'blood_group', 'has_criminal_record', 'has_administrative_offense',
                       )
        }),
        ('Антропометричні дані', {
            'classes': ('grp-collapse grp-closed',),
            'fields': ('height', 'weight', 'arm_span', 'leg_span', 'chest_circumference', 'waist_circumference', 'hip_circumference')
        }),
        ('Батько', {
            'classes': ('grp-collapse grp-closed',),
            'fields': ('father_last_name', 'father_first_name', 'father_middle_name')
        }),
        ('Мати', {
            'classes': ('grp-collapse grp-closed',),
            'fields': ('mother_last_name', 'mother_first_name', 'mother_middle_name')
        }),
        ('Чоловік/Дружина', {
            'classes': ('grp-collapse grp-closed',),
            'fields': ('family_status', 'spouse_last_name', 'spouse_first_name', 'spouse_middle_name')
        }),
    )
