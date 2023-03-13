# Generated by Django 4.1.7 on 2023-03-06 19:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_delete_grouporganization_remove_coreuser_av_color_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='coreuser',
            name='organization',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='core.coreorganization', verbose_name='Організація'),
        ),
    ]