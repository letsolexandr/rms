# Generated by Django 4.1.7 on 2023-03-02 13:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mrs', '0010_alter_militaryperson_blood_group'),
    ]

    operations = [
        migrations.AlterField(
            model_name='militaryperson',
            name='passport_number',
            field=models.CharField(db_index=True, max_length=6, verbose_name='Номер паспорту'),
        ),
        migrations.AlterField(
            model_name='militaryperson',
            name='taxpayer_id',
            field=models.CharField(blank=True, db_index=True, max_length=10, null=True, verbose_name='РНОКПП'),
        ),
    ]
