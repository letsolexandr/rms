# Generated by Django 3.1 on 2023-02-15 20:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('audit', '0002_auto_20230112_1541'),
    ]

    operations = [
        migrations.AddField(
            model_name='loginevent',
            name='comment',
            field=models.CharField(max_length=300, null=True, verbose_name='Коментар'),
        ),
    ]