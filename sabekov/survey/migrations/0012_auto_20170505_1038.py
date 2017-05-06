# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-05-05 08:38
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0011_auto_20170503_2124'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='checklist',
            name='catalogs',
        ),
        migrations.RemoveField(
            model_name='checklist',
            name='sequence',
        ),
        migrations.AddField(
            model_name='catalog',
            name='checklist',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='catalogs', to='survey.Checklist'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='catalog',
            name='is_top_level',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterOrderWithRespectTo(
            name='catalog',
            order_with_respect_to='checklist',
        ),
    ]