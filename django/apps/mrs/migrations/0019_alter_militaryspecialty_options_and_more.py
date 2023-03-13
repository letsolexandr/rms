# Generated by Django 4.1.7 on 2023-03-06 09:56

import apps.mrs.models
import django.contrib.postgres.indexes
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_delete_grouporganization_remove_coreuser_av_color_and_more'),
        ('mrs', '0018_tckemployee'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='militaryspecialty',
            options={'verbose_name': 'Військово-облікова спеціальність', 'verbose_name_plural': 'Військово-облікові спеціальністі'},
        ),
        migrations.AlterModelOptions(
            name='tckemployee',
            options={'verbose_name': 'ТЦК СП обліку', 'verbose_name_plural': 'ТЦК СП обліку'},
        ),
        migrations.AddField(
            model_name='militaryperson',
            name='tcks',
            field=models.ManyToManyField(through='mrs.TCKEmployee', to='core.coreorganization'),
        ),
        migrations.AddField(
            model_name='noticedelivery',
            name='result_file',
            field=models.FileField(blank=True, null=True, upload_to='uploads/notice_result/', verbose_name='Файл підтвердження'),
        ),
        migrations.AlterField(
            model_name='militaryperson',
            name='gender',
            field=models.CharField(choices=[('M', 'Чоловік'), ('F', 'Жінка')], default='M', max_length=1, verbose_name='Стать'),
        ),
        migrations.AlterField(
            model_name='mobilizationpostponementdoc',
            name='detail_file',
            field=models.FileField(upload_to='uploads/mobilization_postponement_doc/', verbose_name='Копія документа що підтверджеє відстрочку'),
        ),
        migrations.AlterField(
            model_name='noticedelivery',
            name='send_on_save',
            field=models.BooleanField(default=True, help_text='** Автоматична відправка буде здійснена якщо обрати месенджер, або електронну пошту', verbose_name='Відправити автоматично при збереженні'),
        ),
        migrations.AlterField(
            model_name='tckemployee',
            name='tck',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='core.coreorganization', verbose_name='ТЦК СП'),
        ),
        migrations.AddIndex(
            model_name='company',
            index=django.contrib.postgres.indexes.GinIndex(fields=['edrpou'], name='edrpou_gin_index', opclasses=['gin_trgm_ops']),
        ),
        migrations.AddIndex(
            model_name='company',
            index=apps.mrs.models.UpperIndex(fields=['edrpou'], name='edrpou_upper_index'),
        ),
        migrations.AddIndex(
            model_name='company',
            index=apps.mrs.models.UpperGinIndex(fields=['edrpou'], name='edrpou_gin_upper_index', opclasses=['gin_trgm_ops']),
        ),
        migrations.AddIndex(
            model_name='company',
            index=django.contrib.postgres.indexes.HashIndex(fields=['edrpou'], name='edrpou_hash_index'),
        ),
        migrations.AddIndex(
            model_name='company',
            index=apps.mrs.models.UpperIndex(fields=['full_name'], name='full_name_index'),
        ),
        migrations.AddIndex(
            model_name='company',
            index=apps.mrs.models.UpperGinIndex(fields=['full_name'], name='full_name_gin_upper_index', opclasses=['gin_trgm_ops']),
        ),
        migrations.AddIndex(
            model_name='company',
            index=apps.mrs.models.UpperIndex(fields=['name'], name='name_index'),
        ),
        migrations.AddIndex(
            model_name='company',
            index=apps.mrs.models.UpperGinIndex(fields=['name'], name='name_gin_upper_index', opclasses=['gin_trgm_ops']),
        ),
    ]