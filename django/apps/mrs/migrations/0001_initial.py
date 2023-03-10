# Generated by Django 3.1 on 2023-02-25 13:36

import apps.core.mixins
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='BloodType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('group', models.CharField(choices=[('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'), ('AB+', 'AB+'), ('AB-', 'AB-'), ('O+', 'O+'), ('O-', 'O-')], max_length=3)),
                ('rhesus', models.CharField(choices=[('+', '+'), ('-', '-')], max_length=1)),
            ],
            options={
                'verbose_name': 'Група крові',
                'verbose_name_plural': 'Групи крові',
            },
        ),
        migrations.CreateModel(
            name='MilitaryPerson',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_deleted', models.BooleanField(db_index=True, default=False, editable=False, verbose_name='**Дані помічено на видалення?')),
                ('unique_uuid', models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, help_text='Інформацію, відмічену за допомогою UUID, можна використовувати без необхідності вирішення конфлікту імен', verbose_name='**Унікальний ідентифікатор запису, в загальному просторі імен')),
                ('date_add', models.DateTimeField(auto_now_add=True, db_index=True, null=True, verbose_name='**Дата створення')),
                ('date_edit', models.DateTimeField(auto_now=True, db_index=True, null=True, verbose_name='**Дата останньої зміни')),
                ('author_display_name', models.TextField(editable=False, null=True, verbose_name='**Автор')),
                ('editor_display_name', models.TextField(editable=False, null=True, verbose_name='**Останій редактор(відображення)')),
                ('last_name', models.CharField(max_length=255, verbose_name='Прізвище')),
                ('first_name', models.CharField(max_length=255, verbose_name="Ім'я")),
                ('middle_name', models.CharField(blank=True, max_length=255, null=True, verbose_name='По-батькові')),
                ('date_of_birth', models.DateField(verbose_name='Дата народження')),
                ('place_of_birth', models.CharField(max_length=100, verbose_name='Місце ранодження')),
                ('gender', models.CharField(choices=[('M', 'Чоловік'), ('F', 'Жінка')], max_length=1, verbose_name='Стать')),
                ('residence_address', models.CharField(max_length=255, verbose_name='Адреса реєстрації')),
                ('current_address', models.CharField(max_length=255, verbose_name='Адреса проживання')),
                ('father_last_name', models.CharField(blank=True, max_length=100, null=True, verbose_name='Прізвище')),
                ('father_first_name', models.CharField(blank=True, max_length=100, null=True, verbose_name="Ім'я")),
                ('father_middle_name', models.CharField(blank=True, max_length=100, null=True, verbose_name='По-батькові')),
                ('father_date_of_birth', models.DateField(blank=True, null=True, verbose_name='Дата народження')),
                ('mother_last_name', models.CharField(blank=True, max_length=100, null=True, verbose_name='Прізвище')),
                ('mother_first_name', models.CharField(blank=True, max_length=100, null=True, verbose_name="Ім'я")),
                ('mother_middle_name', models.CharField(blank=True, max_length=100, null=True, verbose_name='По-батькові')),
                ('mother_date_of_birth', models.DateField(blank=True, null=True, verbose_name='Дата народження')),
                ('spouse_last_name', models.CharField(blank=True, max_length=100, null=True, verbose_name='Прізвище')),
                ('spouse_first_name', models.CharField(blank=True, max_length=100, null=True, verbose_name="Ім'я")),
                ('spouse_middle_name', models.CharField(blank=True, max_length=100, null=True, verbose_name='По-батькові')),
                ('spouse_date_of_birth', models.DateField(blank=True, null=True, verbose_name='Дата народження')),
                ('passport_series', models.CharField(max_length=2)),
                ('passport_number', models.CharField(max_length=6)),
                ('passport_issue_date', models.DateField()),
                ('passport_issuing_authority', models.CharField(max_length=255)),
                ('passport_expiration_date', models.DateField(blank=True, null=True)),
                ('taxpayer_id', models.CharField(blank=True, max_length=10, null=True)),
                ('photo', models.ImageField(blank=True, null=True, upload_to='military_photos/')),
                ('disability_group', models.CharField(choices=[('I', 'I група'), ('II', 'II група'), ('III', 'III група'), ('IV', 'IV група'), ('N', 'немає інвалідності')], default='N', max_length=3, verbose_name='Група інвалідності')),
                ('military_education_level', models.CharField(choices=[('SE', 'Середня загальна освіта'), ('VO', 'Професійно-технічна освіта'), ('HI', 'Вища освіта'), ('PG', 'Післядипломна освіта')], max_length=10, verbose_name='Рівень військової освіти')),
                ('reserve_category', models.CharField(choices=[('A', 'Категорія А'), ('B', 'Категорія Б'), ('C', 'Категорія В')], max_length=1, verbose_name='Категорія запасу')),
                ('accounting_group', models.CharField(choices=[('AD', 'Військовослужбовець строкової служби'), ('CS', 'Військовослужбовець контрактної служби'), ('R', "Військовозобов'язаний запасу"), ('NG', 'Військовослужбовець Національної гвардії'), ('TD', 'Військовослужбовець територіальної оборони'), ('O', 'Інше')], max_length=10, verbose_name='Група обліку')),
                ('family_status', models.CharField(choices=[('S', 'Неодружений/неодружена'), ('M', 'Одружений/одружена'), ('D', 'Розлучений/розлучена'), ('W', 'Вдівець/вдова')], max_length=100, verbose_name='Сімейний стан')),
                ('health_status', models.CharField(choices=[('A1', 'Здатний до призову'), ('A2', 'Обмежено здатний до призову'), ('B', 'Тимчасово нездатний до призову'), ('C', 'Постійно нездатний до призову')], max_length=100, verbose_name='Ступінь придатності до військової служби за станом здоров’я')),
                ('has_criminal_record', models.BooleanField(default=False, verbose_name='Наявність чи відсутність судимості')),
                ('has_administrative_offense', models.BooleanField(default=False, verbose_name='Притягнення до адміністративної відповідальності за порушення правил військового обліку')),
                ('height', models.FloatField(verbose_name='Зріст')),
                ('weight', models.FloatField(verbose_name='Вага')),
                ('arm_span', models.FloatField(verbose_name='Розмах рук')),
                ('leg_span', models.FloatField(verbose_name='Розмах ніг')),
                ('chest_circumference', models.FloatField(verbose_name='Обхват грудної клітки')),
                ('waist_circumference', models.FloatField(verbose_name='Обхват талії')),
                ('hip_circumference', models.FloatField(verbose_name='Обхват стегон')),
                ('author', models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='militaryperson_author', to=settings.AUTH_USER_MODEL, verbose_name='**Автор')),
                ('blood_group', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='mrs.bloodtype', verbose_name='Група крові та резус фактор')),
                ('editor', models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='militaryperson_editor', to=settings.AUTH_USER_MODEL, verbose_name='**Останій редактор')),
            ],
            options={
                'abstract': False,
            },
            bases=(apps.core.mixins.CheckProtected, apps.core.mixins.RelatedObjects, models.Model),
        ),
        migrations.CreateModel(
            name='MilitaryRank',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, verbose_name='Назва')),
                ('short_name', models.CharField(max_length=10, verbose_name='Скорочена назва')),
            ],
            options={
                'verbose_name': 'Військове звання',
                'verbose_name_plural': 'Військові звання',
            },
        ),
        migrations.CreateModel(
            name='MilitarySpecialty',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=10, unique=True)),
                ('title', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='MobilizationPostponement',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reason', models.CharField(choices=[('ST', 'навчання'), ('WO', 'робота'), ('FA', 'сімейні обставини'), ('HE', "стан здоров'я"), ('OT', 'інша підстава')], max_length=2, verbose_name='Підстава відстрочки')),
                ('details', models.TextField(blank=True, verbose_name='Деталізація підстави')),
                ('detail_file', models.FileField(blank=True, upload_to='', verbose_name='Копія документа що підтверджеє відстрочку')),
                ('start_date', models.DateField(blank=True, null=True, verbose_name='Початок дії')),
                ('expiration_date', models.DateField(blank=True, null=True, verbose_name='Кінець дії')),
                ('military_person', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mrs.militaryperson')),
            ],
            options={
                'verbose_name': 'Підстава відстрочки від мобілізації',
                'verbose_name_plural': 'Підстави відстрочок від мобілізації',
            },
        ),
        migrations.CreateModel(
            name='MilitaryRegistrationViolation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('violation_date', models.DateField()),
                ('violation_description', models.TextField()),
                ('military_person', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mrs.militaryperson')),
            ],
            options={
                'verbose_name': 'Порушення правил військового обліку',
                'verbose_name_plural': 'Порушення правил військового обліку',
            },
        ),
        migrations.AddField(
            model_name='militaryperson',
            name='military_rank',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='mrs.militaryrank', verbose_name='Військове звання'),
        ),
        migrations.AddField(
            model_name='militaryperson',
            name='military_specialty',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='mrs.militaryspecialty', verbose_name='Військово-облікова спеціальність'),
        ),
        migrations.AddField(
            model_name='militaryperson',
            name='organization',
            field=models.ForeignKey(editable=False, help_text='До якої організації відноситься інформація', null=True, on_delete=django.db.models.deletion.PROTECT, to='core.coreorganization', verbose_name='**Організація'),
        ),
        migrations.CreateModel(
            name='MilitaryMovement',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_deleted', models.BooleanField(db_index=True, default=False, editable=False, verbose_name='**Дані помічено на видалення?')),
                ('unique_uuid', models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, help_text='Інформацію, відмічену за допомогою UUID, можна використовувати без необхідності вирішення конфлікту імен', verbose_name='**Унікальний ідентифікатор запису, в загальному просторі імен')),
                ('date_add', models.DateTimeField(auto_now_add=True, db_index=True, null=True, verbose_name='**Дата створення')),
                ('date_edit', models.DateTimeField(auto_now=True, db_index=True, null=True, verbose_name='**Дата останньої зміни')),
                ('author_display_name', models.TextField(editable=False, null=True, verbose_name='**Автор')),
                ('editor_display_name', models.TextField(editable=False, null=True, verbose_name='**Останій редактор(відображення)')),
                ('departure_date', models.DateField(verbose_name='дата  виїзду')),
                ('destination_country', models.CharField(max_length=255, verbose_name='Країна')),
                ('return_date', models.DateField(blank=True, null=True, verbose_name='дата повернення')),
                ('author', models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='militarymovement_author', to=settings.AUTH_USER_MODEL, verbose_name='**Автор')),
                ('editor', models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='militarymovement_editor', to=settings.AUTH_USER_MODEL, verbose_name='**Останій редактор')),
                ('military_person', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mrs.militaryperson')),
                ('organization', models.ForeignKey(editable=False, help_text='До якої організації відноситься інформація', null=True, on_delete=django.db.models.deletion.PROTECT, to='core.coreorganization', verbose_name='**Організація')),
            ],
            options={
                'abstract': False,
            },
            bases=(apps.core.mixins.CheckProtected, apps.core.mixins.RelatedObjects, models.Model),
        ),
        migrations.CreateModel(
            name='Language',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_deleted', models.BooleanField(db_index=True, default=False, editable=False, verbose_name='**Дані помічено на видалення?')),
                ('unique_uuid', models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, help_text='Інформацію, відмічену за допомогою UUID, можна використовувати без необхідності вирішення конфлікту імен', verbose_name='**Унікальний ідентифікатор запису, в загальному просторі імен')),
                ('date_add', models.DateTimeField(auto_now_add=True, db_index=True, null=True, verbose_name='**Дата створення')),
                ('date_edit', models.DateTimeField(auto_now=True, db_index=True, null=True, verbose_name='**Дата останньої зміни')),
                ('author_display_name', models.TextField(editable=False, null=True, verbose_name='**Автор')),
                ('editor_display_name', models.TextField(editable=False, null=True, verbose_name='**Останій редактор(відображення)')),
                ('code', models.CharField(max_length=10)),
                ('name', models.CharField(max_length=255)),
                ('author', models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='language_author', to=settings.AUTH_USER_MODEL, verbose_name='**Автор')),
                ('editor', models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='language_editor', to=settings.AUTH_USER_MODEL, verbose_name='**Останій редактор')),
                ('organization', models.ForeignKey(editable=False, help_text='До якої організації відноситься інформація', null=True, on_delete=django.db.models.deletion.PROTECT, to='core.coreorganization', verbose_name='**Організація')),
            ],
            options={
                'abstract': False,
            },
            bases=(apps.core.mixins.CheckProtected, apps.core.mixins.RelatedObjects, models.Model),
        ),
        migrations.CreateModel(
            name='ForeignLanguage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_deleted', models.BooleanField(db_index=True, default=False, editable=False, verbose_name='**Дані помічено на видалення?')),
                ('unique_uuid', models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, help_text='Інформацію, відмічену за допомогою UUID, можна використовувати без необхідності вирішення конфлікту імен', verbose_name='**Унікальний ідентифікатор запису, в загальному просторі імен')),
                ('date_add', models.DateTimeField(auto_now_add=True, db_index=True, null=True, verbose_name='**Дата створення')),
                ('date_edit', models.DateTimeField(auto_now=True, db_index=True, null=True, verbose_name='**Дата останньої зміни')),
                ('author_display_name', models.TextField(editable=False, null=True, verbose_name='**Автор')),
                ('editor_display_name', models.TextField(editable=False, null=True, verbose_name='**Останій редактор(відображення)')),
                ('language_level', models.CharField(choices=[('A1', 'Elementary'), ('A2', 'Pre-Intermediate'), ('B1', 'Intermediate'), ('B2', 'Upper-Intermediate'), ('C1', 'Advanced'), ('C2', 'Proficient')], max_length=2)),
                ('author', models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='foreignlanguage_author', to=settings.AUTH_USER_MODEL, verbose_name='**Автор')),
                ('editor', models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='foreignlanguage_editor', to=settings.AUTH_USER_MODEL, verbose_name='**Останій редактор')),
                ('language', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='mrs.language')),
                ('military_person', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mrs.militaryperson')),
                ('organization', models.ForeignKey(editable=False, help_text='До якої організації відноситься інформація', null=True, on_delete=django.db.models.deletion.PROTECT, to='core.coreorganization', verbose_name='**Організація')),
            ],
            options={
                'abstract': False,
            },
            bases=(apps.core.mixins.CheckProtected, apps.core.mixins.RelatedObjects, models.Model),
        ),
        migrations.CreateModel(
            name='Education',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_deleted', models.BooleanField(db_index=True, default=False, editable=False, verbose_name='**Дані помічено на видалення?')),
                ('unique_uuid', models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, help_text='Інформацію, відмічену за допомогою UUID, можна використовувати без необхідності вирішення конфлікту імен', verbose_name='**Унікальний ідентифікатор запису, в загальному просторі імен')),
                ('date_add', models.DateTimeField(auto_now_add=True, db_index=True, null=True, verbose_name='**Дата створення')),
                ('date_edit', models.DateTimeField(auto_now=True, db_index=True, null=True, verbose_name='**Дата останньої зміни')),
                ('author_display_name', models.TextField(editable=False, null=True, verbose_name='**Автор')),
                ('editor_display_name', models.TextField(editable=False, null=True, verbose_name='**Останій редактор(відображення)')),
                ('education', models.CharField(max_length=255)),
                ('specialty', models.CharField(max_length=255)),
                ('author', models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='education_author', to=settings.AUTH_USER_MODEL, verbose_name='**Автор')),
                ('editor', models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='education_editor', to=settings.AUTH_USER_MODEL, verbose_name='**Останій редактор')),
                ('military_person', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mrs.militaryperson')),
                ('organization', models.ForeignKey(editable=False, help_text='До якої організації відноситься інформація', null=True, on_delete=django.db.models.deletion.PROTECT, to='core.coreorganization', verbose_name='**Організація')),
            ],
            options={
                'abstract': False,
            },
            bases=(apps.core.mixins.CheckProtected, apps.core.mixins.RelatedObjects, models.Model),
        ),
        migrations.CreateModel(
            name='Child',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_deleted', models.BooleanField(db_index=True, default=False, editable=False, verbose_name='**Дані помічено на видалення?')),
                ('unique_uuid', models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, help_text='Інформацію, відмічену за допомогою UUID, можна використовувати без необхідності вирішення конфлікту імен', verbose_name='**Унікальний ідентифікатор запису, в загальному просторі імен')),
                ('date_add', models.DateTimeField(auto_now_add=True, db_index=True, null=True, verbose_name='**Дата створення')),
                ('date_edit', models.DateTimeField(auto_now=True, db_index=True, null=True, verbose_name='**Дата останньої зміни')),
                ('author_display_name', models.TextField(editable=False, null=True, verbose_name='**Автор')),
                ('editor_display_name', models.TextField(editable=False, null=True, verbose_name='**Останій редактор(відображення)')),
                ('last_name', models.CharField(max_length=100)),
                ('first_name', models.CharField(max_length=100)),
                ('middle_name', models.CharField(blank=True, max_length=100, null=True)),
                ('date_of_birth', models.DateField()),
                ('author', models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='child_author', to=settings.AUTH_USER_MODEL, verbose_name='**Автор')),
                ('editor', models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='child_editor', to=settings.AUTH_USER_MODEL, verbose_name='**Останій редактор')),
                ('military_person', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mrs.militaryperson')),
                ('organization', models.ForeignKey(editable=False, help_text='До якої організації відноситься інформація', null=True, on_delete=django.db.models.deletion.PROTECT, to='core.coreorganization', verbose_name='**Організація')),
            ],
            options={
                'abstract': False,
            },
            bases=(apps.core.mixins.CheckProtected, apps.core.mixins.RelatedObjects, models.Model),
        ),
    ]
