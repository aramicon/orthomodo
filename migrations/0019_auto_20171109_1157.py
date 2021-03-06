# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-11-09 11:57
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('orthomodoweb', '0018_auto_20171109_1157'),
    ]

    operations = [
        migrations.AddField(
            model_name='orthomodojob',
            name='is_poured',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='orthomodojob',
            name='is_poured_marked_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='orthomodojob_is_poured_marked_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='orthomodojob',
            name='is_poured_marked_when',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='orthomodojob',
            name='poured_date',
            field=models.DateField(blank=True, null=True),
        ),
    ]
