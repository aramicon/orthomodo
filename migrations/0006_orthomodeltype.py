# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-10-13 15:09
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orthomodoweb', '0005_clinician'),
    ]

    operations = [
        migrations.CreateModel(
            name='OrthoModelType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=20, unique=True)),
                ('name', models.CharField(max_length=200)),
                ('description', models.TextField(blank=True)),
                ('date_updated', models.DateTimeField(auto_now=True, verbose_name='Date updated')),
                ('date_created', models.DateTimeField(auto_now_add=True, verbose_name='Date Created')),
            ],
        ),
    ]
