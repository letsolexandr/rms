# Generated by Django 4.1.7 on 2023-03-02 15:00

import django.contrib.postgres.search
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mrs', '0011_alter_militaryperson_passport_number_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='militaryperson',
            name='search_vector',
            field=django.contrib.postgres.search.SearchVectorField(null=True),
        ),
    ]
