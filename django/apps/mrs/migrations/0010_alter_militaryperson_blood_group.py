# Generated by Django 4.1.7 on 2023-03-02 12:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mrs', '0009_alter_mobilizationpostponementdoc_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='militaryperson',
            name='blood_group',
            field=models.CharField(choices=[('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'), ('AB+', 'AB+'), ('AB-', 'AB-'), ('O+', 'O+'), ('O-', 'O-')], default='A-', max_length=5, verbose_name='Група крові та резус фактор'),
        ),
    ]
