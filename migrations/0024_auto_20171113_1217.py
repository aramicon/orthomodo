# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-11-13 12:17
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orthomodoweb', '0023_auto_20171113_1216'),
    ]

    operations = [
        migrations.AlterField(
            model_name='createdmodeluse',
            name='code',
            field=models.CharField(max_length=20, unique=True),
        ),
    ]
