# Generated by Django 2.2.10 on 2020-06-24 19:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_add_primary_activity'),
    ]

    operations = [
        migrations.AddField(
            model_name='company',
            name='server_id',
            field=models.IntegerField(blank=True, null=True, unique=True),
        ),
        migrations.AddField(
            model_name='user',
            name='server_id',
            field=models.IntegerField(blank=True, null=True, unique=True),
        ),
    ]
