# Generated by Django 2.2.10 on 2020-03-05 05:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_create_company_model'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='company',
            options={'verbose_name_plural': 'Companies'},
        ),
    ]