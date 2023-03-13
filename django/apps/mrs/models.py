from django.db import models
from django.contrib.postgres.search import SearchVectorField
from django.contrib.postgres.indexes import GinIndex, HashIndex
from apps.core.models import CoreBase, SystemFieldsMixin, PersonIdentityMixin, CoreOrganization


class UpperIndex(models.Index):
    def create_sql(self, model, schema_editor, using='', **kwargs):
        statement = super().create_sql(
            model, schema_editor, using, **kwargs
        )
        quote_name = statement.parts['columns'].quote_name

        def upper_quoted(column):
            return 'UPPER({0})'.format(quote_name(column))

        statement.parts['columns'].quote_name = upper_quoted
        return statement


class UpperGinIndex(GinIndex):

    def create_sql(self, model, schema_editor, using='', **kwargs):
        statement = super().create_sql(
            model, schema_editor, using, **kwargs
        )
        quote_name = statement.parts['columns'].quote_name

        def upper_quoted(column):
            return 'UPPER({0})'.format(quote_name(column))

        statement.parts['columns'].quote_name = upper_quoted
        return statement


class FitnessDegree(models.TextChoices):
    A1 = 'A1', 'Здатний до призову'
    A2 = 'A2', 'Обмежено здатний до призову'
    B = 'B', 'Тимчасово нездатний до призову'
    C = 'C', 'Постійно нездатний до призову'


class ReserveCategoryChoices(models.TextChoices):
    CATEGORY_A = 'A', 'Категорія А'
    CATEGORY_B = 'B', 'Категорія Б'
    CATEGORY_C = 'C', 'Категорія В'


class EducationLevel(models.TextChoices):
    SECONDARY = 'SE', 'Середня загальна освіта'
    VOCATIONAL = 'VO', 'Професійно-технічна освіта'
    HIGHER = 'HI', 'Вища освіта'
    POSTGRADUATE = 'PG', 'Післядипломна освіта'
    NONE = 'NO', 'Відсутня'


class MilitarySpecialty(models.Model):
    code = models.CharField(max_length=10, unique=True)
    title = models.CharField(max_length=255)


    class Meta:
        verbose_name = 'Військово-облікова спеціальність'
        verbose_name_plural = 'Військово-облікові спеціальністі'

    def __str__(self):
        return f"{self.code} - {self.title}"


class MilitaryAccountingGroup(models.TextChoices):
    ACTIVE_DUTY = 'AD', 'Військовослужбовець строкової служби'
    CONTRACT_SERVICE = 'CS', 'Військовослужбовець контрактної служби'
    RESERVE = 'R', 'Військовозобов\'язаний запасу'
    NATIONAL_GUARD = 'NG', 'Військовослужбовець Національної гвардії'
    TERRITORIAL_DEFENSE = 'TD', 'Військовослужбовець територіальної оборони'
    OTHER = 'O', 'Інше'


class DisabilityGroup(models.TextChoices):
    GROUP_I = 'I', 'I група'
    GROUP_II = 'II', 'II група'
    GROUP_III = 'III', 'III група'
    GROUP_IV = 'IV', 'IV група'
    NO_DISABILITY = 'N', 'немає інвалідності'


class MilitaryRank(models.Model):
    name = models.CharField(max_length=50, verbose_name='Назва')
    short_name = models.CharField(
        max_length=10, verbose_name='Скорочена назва')

    class Meta:
        verbose_name = 'Військове звання'
        verbose_name_plural = 'Військові звання'

    def __str__(self):
        return self.name


class BloodGroup(models.TextChoices):
    A_POSITIVE = 'A+', 'A+'
    A_NEGATIVE = 'A-', 'A-'
    B_POSITIVE = 'B+', 'B+'
    B_NEGATIVE = 'B-', 'B-'
    AB_POSITIVE = 'AB+', 'AB+'
    AB_NEGATIVE = 'AB-', 'AB-'
    O_POSITIVE = 'O+', 'O+'
    O_NEGATIVE = 'O-', 'O-'


class FamilyStatus(models.TextChoices):
    SINGLE = 'S', 'Неодружений/неодружена'
    MARRIED = 'M', 'Одружений/одружена'
    DIVORCED = 'D', 'Розлучений/розлучена'
    WIDOWED = 'W', 'Вдівець/вдова'






class Gender(models.TextChoices):
    M = 'M', 'Чоловік'
    F= 'F', 'Жінка'

class MilitaryPerson(CoreBase):
    last_name = models.CharField(max_length=255, verbose_name="Прізвище", db_index=True)
    first_name = models.CharField(max_length=255, verbose_name="Ім'я", db_index=True)
    middle_name = models.CharField(
        max_length=255, blank=True, null=True, verbose_name="По-батькові", db_index=True)
    date_of_birth = models.DateField(verbose_name="Дата народження", db_index=True)
    place_of_birth = models.CharField(
        max_length=100, verbose_name="Місце народження")
    gender = models.CharField(max_length=1, choices=Gender.choices, default=Gender.M, verbose_name="Стать")
    residence_address = models.CharField(
        max_length=255, verbose_name="Адреса реєстрації")
    current_address = models.CharField(
        max_length=255, verbose_name="Адреса проживання")
    # Батько
    father_last_name = models.CharField(
        max_length=100, blank=True, null=True, verbose_name="Прізвище")
    father_first_name = models.CharField(
        max_length=100, blank=True, null=True, verbose_name="Ім'я")
    father_middle_name = models.CharField(
        max_length=100, blank=True, null=True, verbose_name="По-батькові")
    father_date_of_birth = models.DateField(
        blank=True, null=True, verbose_name="Дата народження")
    # Мати
    mother_last_name = models.CharField(
        max_length=100, blank=True, null=True, verbose_name="Прізвище")
    mother_first_name = models.CharField(
        max_length=100, blank=True, null=True, verbose_name="Ім'я")
    mother_middle_name = models.CharField(
        max_length=100, blank=True, null=True, verbose_name="По-батькові")
    mother_date_of_birth = models.DateField(
        blank=True, null=True, verbose_name="Дата народження")
    # Подружжя
    spouse_last_name = models.CharField(
        max_length=100, blank=True, null=True, verbose_name="Прізвище")
    spouse_first_name = models.CharField(
        max_length=100, blank=True, null=True, verbose_name="Ім'я")
    spouse_middle_name = models.CharField(
        max_length=100, blank=True, null=True, verbose_name="По-батькові")
    spouse_date_of_birth = models.DateField(
        blank=True, null=True, verbose_name="Дата народження")
    # Паспортні дані
    passport_series = models.CharField(
        max_length=2, verbose_name="Серія паспорт")
    passport_number = models.CharField(
        max_length=6, verbose_name="Номер паспорту", db_index=True)
    passport_issue_date = models.DateField(verbose_name="Дата видачі")
    passport_issuing_authority = models.CharField(
        max_length=255, verbose_name="Виданий")
    passport_expiration_date = models.DateField(
        blank=True, null=True, verbose_name="Закінчення дії")
    taxpayer_id = models.CharField(
        max_length=10, blank=True, null=True, verbose_name="РНОКПП", db_index=True)
    photo = models.ImageField(
        upload_to='uploads/military_photos/', blank=True, null=True, verbose_name="ФОТО")

    # Дані військового обліку
    military_rank = models.ForeignKey(
        MilitaryRank, verbose_name='Військове звання', on_delete=models.PROTECT, null=True, blank=True)
    military_specialty = models.ForeignKey(
        MilitarySpecialty, verbose_name='Військово-облікова спеціальність', on_delete=models.PROTECT, null=True, blank=True)
    military_education_level = models.CharField(
        max_length=10, choices=EducationLevel.choices, verbose_name='Рівень військової освіти', null=True, default=EducationLevel.NONE)
    reserve_category = models.CharField(
        max_length=1, choices=ReserveCategoryChoices.choices, verbose_name='Категорія запасу', null=True, blank=True)
    accounting_group = models.CharField(
        max_length=10, choices=MilitaryAccountingGroup.choices, verbose_name='Група обліку', null=True, blank=True)
    family_status = models.CharField(
        max_length=100, choices=FamilyStatus.choices, default=FamilyStatus.SINGLE, verbose_name='Сімейний стан')
    disability_group = models.CharField(max_length=3, choices=DisabilityGroup.choices,
                                        default=DisabilityGroup.NO_DISABILITY, verbose_name="Група інвалідності",db_index=True)
    health_status = models.CharField(max_length=100, verbose_name='Ступінь придатності до військової служби за станом здоров’я',
                                     choices=FitnessDegree.choices, default=FitnessDegree.A1,db_index=True)
    blood_group = models.CharField(max_length=5, verbose_name='Група крові та резус фактор',
                                   choices=BloodGroup.choices, default=BloodGroup.A_NEGATIVE, db_index=True)
    has_criminal_record = models.BooleanField(
        default=False, verbose_name='Наявність чи відсутність судимості')
    has_administrative_offense = models.BooleanField(
        default=False, verbose_name='Притягнення до адміністративної відповідальності за порушення правил військового обліку')
    # Антропометричні дані'
    height = models.FloatField(verbose_name='Зріст')
    weight = models.FloatField(verbose_name='Вага')
    arm_span = models.FloatField(verbose_name='Розмах рук')
    leg_span = models.FloatField(verbose_name='Розмах ніг')
    chest_circumference = models.FloatField(
        verbose_name='Обхват грудної клітки')
    waist_circumference = models.FloatField(verbose_name='Обхват талії')
    hip_circumference = models.FloatField(verbose_name='Обхват стегон')
    search_vector = SearchVectorField(null=True)
    tcks = models.ManyToManyField(CoreOrganization, through="TCKEmployee")

    class Meta:
        verbose_name = "Віськовозобов`язаний"
        verbose_name_plural = "Віськовозобов`язані особи"
        indexes = [
            GinIndex(fields=['taxpayer_id'], name='taxpayer_id_gin_index',
                     opclasses=['gin_trgm_ops']),
            GinIndex(fields=['passport_number'], name='passport_number_gin_index',
                     opclasses=['gin_trgm_ops']),
            UpperIndex(fields=['taxpayer_id'],
                       name='taxpayer_id_upper_index'),
            UpperGinIndex(fields=['taxpayer_id'], name='taxpayer_id_gin_upper_index',
                          opclasses=['gin_trgm_ops']),
            UpperIndex(fields=['passport_number'],
                       name='passport_number_upper_index'),
            UpperGinIndex(fields=['passport_number'], name='pass_n_gin_upper_index',
                          opclasses=['gin_trgm_ops']),
            HashIndex(fields=['taxpayer_id'], name='taxpayer_id_hash_index'),
            HashIndex(fields=['passport_number'],
                      name='passport_number_hash_index'),

        ]

    def __str__(self):
        return f"{self.taxpayer_id or f'{self.passport_series}: {self.passport_number}'}: {self.last_name} {self.first_name}"


class MilitaryPersonPhone(CoreBase):
    military_person = models.ForeignKey(
        MilitaryPerson, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20, verbose_name="Телефон")

    class Meta:
        verbose_name = "Телефон"
        verbose_name_plural = "Контактні телефони"

    def __str__(self):
        return f"{self.phone} {self.phone}"


class Child(CoreBase):
    military_person = models.ForeignKey(
        MilitaryPerson, on_delete=models.CASCADE)
    last_name = models.CharField(max_length=100, verbose_name="Прізвище")
    first_name = models.CharField(max_length=100, verbose_name="Ім'я")
    middle_name = models.CharField(
        max_length=100, blank=True, null=True, verbose_name="По-батькові")
    date_of_birth = models.DateField()

    class Meta:
        verbose_name = 'Дитина'
        verbose_name_plural = 'Діти'


class Education(CoreBase):
    military_person = models.ForeignKey(
        MilitaryPerson, on_delete=models.CASCADE)
    education = models.CharField(max_length=255, verbose_name='Напрямок')
    specialty = models.CharField(max_length=255, verbose_name='Спеціальність')

    class Meta:
        verbose_name = 'Навчання у ВУЗі'
        verbose_name_plural = 'Навчання у ВУЗах'


class Language(CoreBase):
    code = models.CharField(max_length=10, verbose_name='Код')
    name = models.CharField(max_length=255, verbose_name='Назва')

    class Meta:
        verbose_name = 'Іноземна мова'
        verbose_name_plural = 'Іноземні мови'


class LanguageLevel(models.TextChoices):
    A1 = 'A1', 'Elementary'
    A2 = 'A2', 'Pre-Intermediate'
    B1 = 'B1', 'Intermediate'
    B2 = 'B2', 'Upper-Intermediate'
    C1 = 'C1', 'Advanced'
    C2 = 'C2', 'Proficient'


class ForeignLanguage(CoreBase):
    military_person = models.ForeignKey(
        MilitaryPerson, on_delete=models.CASCADE)
    language = models.ForeignKey(
        Language, on_delete=models.PROTECT, verbose_name="Мова")
    language_level = models.CharField(
        max_length=2, choices=LanguageLevel.choices, verbose_name="Рівень володіння")

    class Meta:
        verbose_name = 'Знання іноземних мов'
        verbose_name_plural = 'Знання іноземних мов'


class MilitaryMovement(CoreBase):
    military_person = models.ForeignKey(
        MilitaryPerson, on_delete=models.CASCADE)
    departure_date = models.DateField(verbose_name="дата виїзду")
    destination_country = models.CharField(
        max_length=255, verbose_name="Країна")
    return_date = models.DateField(
        null=True, blank=True, verbose_name="дата повернення")

    class Meta:
        verbose_name = "Дані про перетин кордону"
        verbose_name_plural = "Дані про перетин кордону"

    def __str__(self):
        return f"{self.military_person} ({self.destination_country})"


class MilitaryRegistrationViolation(models.Model):
    military_person = models.ForeignKey(
        MilitaryPerson, on_delete=models.CASCADE)
    violation_date = models.DateField()
    violation_description = models.TextField()

    class Meta:
        verbose_name = "Порушення правил військового обліку"
        verbose_name_plural = "Порушення правил військового обліку"


class MobilizationPostponement(models.Model):
    # TODO деталізувати підстави
    class Reason(models.TextChoices):
        STUDY = 'ST', 'навчання'
        WORK = 'WO', 'робота'
        FAMILY = 'FA', 'сімейні обставини'
        HEALTH = 'HE', 'стан здоров\'я'
        OTHER = 'OT', 'інша підстава'
    military_person = models.ForeignKey(
        MilitaryPerson, on_delete=models.CASCADE)

    reason = models.CharField(
        max_length=2, choices=Reason.choices, verbose_name='Підстава відстрочки')
    details = models.TextField(blank=True, verbose_name='Деталізація підстави')
    detail_file = models.FileField(
        verbose_name='Копія документа що підтверджеє відстрочку')
    start_date = models.DateField(
        blank=True, null=True, verbose_name='Початок дії')
    expiration_date = models.DateField(
        blank=True, null=True, verbose_name='Кінець дії')

    class Meta:
        verbose_name = 'Відстрочка від мобілізації'
        verbose_name_plural = 'Відстрочки від мобілізації'



class Company(CoreBase):
    name = models.CharField(blank=True, null=True, max_length=256,
                            db_index=True, verbose_name="Назва")
    full_name = models.CharField(db_index=True, max_length=256,
                                 verbose_name="Повна назва")
    address = models.CharField(db_index=True,
                               max_length=200, verbose_name="Адреса")
    edrpou = models.CharField(
        max_length=10, db_index=True, verbose_name="ЄДРПОУ")
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
        verbose_name = 'Роботодавець'
        verbose_name_plural = 'Роботодавці'
        indexes = [
            GinIndex(fields=['edrpou'], name='edrpou_gin_index', opclasses=['gin_trgm_ops']),
            UpperIndex(fields=['edrpou'],  name='edrpou_upper_index'),
            UpperGinIndex(fields=['edrpou'], name='edrpou_gin_upper_index',opclasses=['gin_trgm_ops']),
            HashIndex(fields=['edrpou'], name='edrpou_hash_index'),
            ##############################################################
            UpperIndex(fields=['full_name'], name='full_name_index'),
            UpperGinIndex(fields=['full_name'], name='full_name_gin_upper_index', opclasses=['gin_trgm_ops']),
            ##############################################################
            UpperIndex(fields=['name'], name='name_index'),
            UpperGinIndex(fields=['name'], name='name_gin_upper_index', opclasses=['gin_trgm_ops'])
        ]

    def __str__(self):
        return f"{self.edrpou} : {self.name}"


class CompanyEmployee(CoreBase):
    military_person = models.ForeignKey(
        MilitaryPerson, on_delete=models.PROTECT)
    company = models.ForeignKey(
        Company, on_delete=models.PROTECT, verbose_name="Організація")
    position = models.CharField(max_length=100, verbose_name="Посада")
    hired_date = models.DateField(verbose_name='Прийнятий')
    termination_date = models.DateField(
        blank=True, null=True, verbose_name='Звільнений')

    class Meta:
        verbose_name = 'Місце роботи'
        verbose_name_plural = 'Місця роботи' 
    
    def __str__(self):
        return f"{self.company}"


class TCKEmployee(CoreBase):
    military_person = models.ForeignKey(
        MilitaryPerson, on_delete=models.PROTECT)
    tck = models.ForeignKey(
        CoreOrganization, on_delete=models.PROTECT, verbose_name="ТЦК СП")
    hired_date = models.DateField(verbose_name='Прийнятий на облік')
    termination_date = models.DateField(
        blank=True, null=True, verbose_name='Знятий з обліку')

    class Meta:
        verbose_name = 'ТЦК СП обліку'
        verbose_name_plural = 'ТЦК СП обліку'

    def __str__(self):
        return f"{self.tck}"


class NoticeType(models.TextChoices):
    A1 = 'A1', 'Повістка для уточнення облікових даних'
    A2 = 'A2', 'Повістка для проходження медкомісії'
    A3 = 'A3', 'Повістка-призов до ЗСУ'
    A4 = 'A4', 'Мобілізаційне розпорядження'


class PlaceType(models.TextChoices):
    H = 'H', 'Відправлена за місцем проживання'
    W = 'W', 'Відправлена за місцем роботи'


class DeliveryType(models.TextChoices):
    POST = 'POST', 'Поштою'
    PERSONAL = 'PERSONAL', 'Наручно'
    VIBER = 'VIBER', 'VIBER'
    MAIL = 'MAIL', 'MAIL'


class Notice(CoreBase):
    military_person = models.ForeignKey(
        MilitaryPerson, on_delete=models.PROTECT)
    company = models.ForeignKey(
        Company, on_delete=models.PROTECT, null=True, blank=True, verbose_name="Організація")
    notice_type = models.CharField(
        max_length=2, choices=NoticeType.choices, default=NoticeType.A1, verbose_name="Тип повістки")
    notice_file = models.FileField(
        upload_to='uploads/notice/', verbose_name="Файл повістки")

    class Meta:
        verbose_name = 'Повістка'
        verbose_name_plural = 'Повістки'

    def __str__(self):
        return f"{self.military_person} {self.get_notice_type_display()}"


class NoticeDelivery(models.Model):
    notice = models.ForeignKey(Notice, on_delete=models.PROTECT)
    send_date = models.DateField(
        verbose_name="Дата відправки", null=True, blank=True)
    place_type = models.CharField(
        max_length=1, choices=PlaceType.choices, default=PlaceType.H, verbose_name="Куди направлено")
    delivery_date = models.DateField(
        verbose_name="Дата доставки", null=True, blank=True)
    delivery_type = models.CharField(
        max_length=10, choices=DeliveryType.choices,  verbose_name="Спосіб доставки")
    result_file = models.FileField(upload_to='uploads/notice_result/',null=True, blank=True,
                                   verbose_name="Файл підтвердження",help_text="** Фотофіксація документа що підтверджує доставку" )
    send_on_save = models.BooleanField(
        verbose_name="Відправити автоматично при збереженні", default=False, help_text="** Автоматична відправка буде здійснена якщо обрати месенджер, або електронну пошту")

    class Meta:
        verbose_name = 'Доставка повістки'
        verbose_name_plural = 'Доставка повістки'

class MilitaryTraining(CoreBase):
    military_person = models.ForeignKey(MilitaryPerson, on_delete=models.PROTECT)
    start_date = models.DateField(verbose_name="Дата відправки")
    days_count = models.PositiveIntegerField(verbose_name="Кількість днів")
    military_base = models.CharField(verbose_name="в/ч чи організація", max_length=255)
    military_specialty = models.ForeignKey(MilitarySpecialty, verbose_name='Військово-облікова спеціальність', on_delete=models.PROTECT, null=True,blank=True)
    note = models.CharField(max_length=255,verbose_name="Примітка", null=True,blank=True)

    class Meta:
        verbose_name = 'Навчальні збори'
        verbose_name_plural = 'Навчальні збори'

    def __str__(self):
        return f"{self.military_person} :{self.military_specialty}"


class DocStatus(models.TextChoices):
    NEW = 'NEW', 'Очікує підтвердження'
    SACCESS = 'SACCESS', 'Прийнято'
    DENIED = 'DENIED', 'Відмовлено'


class MobilizationPostponementDocMixin:
    def create_postponement_on_save(self):
        if self.status == DocStatus.SACCESS:
            mp = MobilizationPostponement()
            mp.military_person = self.military_person
            mp.reason = self.reason
            mp.details = self.details
            mp.detail_file = self.detail_file
            mp.start_date = self.start_date
            mp.expiration_date = self.expiration_date
            mp.save()

    def set_military_on_save(self):
        user_taxpayer_id = self.author.ipn
        m_p = MilitaryPerson.objects.filter(taxpayer_id=user_taxpayer_id).first()
        self.military_person = m_p


class MobilizationPostponementDocPermissions(models.TextChoices):
    CAN_REVIEW_STATEMENT = 'can_review_postponement_doc', 'Може розглядати документ про бронювання'

class MobilizationPostponementDoc(PersonIdentityMixin, SystemFieldsMixin,MobilizationPostponementDocMixin):
    # TODO деталізувати підстави
    class Reason(models.TextChoices):
        STUDY = 'ST', 'навчання'
        WORK = 'WO', 'робота'
        FAMILY = 'FA', 'сімейні обставини'
        HEALTH = 'HE', 'стан здоров\'я'
        OTHER = 'OT', 'інша підстава'
    military_person = models.ForeignKey(
        MilitaryPerson, on_delete=models.PROTECT, null=True, blank=True)
    reason = models.CharField(
        max_length=2, choices=Reason.choices, verbose_name='Підстава відстрочки')
    details = models.TextField(blank=True, verbose_name='Деталізація підстави')
    detail_file = models.FileField(
        verbose_name='Копія документа що підтверджеє відстрочку',upload_to='uploads/mobilization_postponement_doc/')
    start_date = models.DateField(
        blank=True, null=True, verbose_name='Початок дії')
    expiration_date = models.DateField(
        blank=True, null=True, verbose_name='Кінець дії')
    status = models.CharField(
        max_length=10, choices=DocStatus.choices, default=DocStatus.NEW, verbose_name='Статус документа')
    reject_reason = models.TextField( null=True, blank=True, verbose_name='Причина відмови')


    class Meta:
        verbose_name = 'Документ про відстрочку (від особи)'
        verbose_name_plural = 'Документи про відстрочку (від особи)'
        permissions = MobilizationPostponementDocPermissions.choices

    def __str__(self):
        return f"Документ про відстрочку: {self.military_person}"

    
    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.set_military_on_save()
        res = super().save(force_insert, force_update, using, update_fields)
        self.create_postponement_on_save()
        return res


class MobilizationPostponementOrgDoc(PersonIdentityMixin, SystemFieldsMixin,MobilizationPostponementDocMixin):
    # TODO деталізувати підстави
    class Reason(models.TextChoices):
        STUDY = 'ST', 'навчання'
        WORK = 'WO', 'робота'
        FAMILY = 'FA', 'сімейні обставини'
        HEALTH = 'HE', 'стан здоров\'я'
        OTHER = 'OT', 'інша підстава'
    military_person = models.ForeignKey(
        MilitaryPerson, on_delete=models.PROTECT, verbose_name='Військовозобовязаний',
        help_text="Пошук за РНОКПП або паспортом")

    reason = models.CharField(
        max_length=2, choices=Reason.choices, verbose_name='Підстава відстрочки')
    details = models.TextField(blank=True, verbose_name='Деталізація підстави')
    detail_file = models.FileField(
        verbose_name='Копія документа що підтверджеє відстрочку')
    start_date = models.DateField(
        blank=True, null=True, verbose_name='Початок дії')
    expiration_date = models.DateField(
        blank=True, null=True, verbose_name='Кінець дії')
    status = models.CharField(
        max_length=10, choices=DocStatus.choices, default=DocStatus.NEW, verbose_name='Статус документа')
    reject_reason = models.TextField( null=True, blank=True, verbose_name='Причина відмови')

    class Meta:
        verbose_name = 'Документ про відстрочку  (від ЮР особи)'
        verbose_name_plural = 'Документи про відстрочку (від ЮР особи)'
        permissions = MobilizationPostponementDocPermissions.choices

    def __str__(self):
        return f"Документ про відстрочку: {self.military_person}"

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        res = super().save(force_insert, force_update, using, update_fields)
        self.create_postponement_on_save()
        return res

