# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-05-06 12:48
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0014_auto_20170505_1416'),
    ]

    operations = [
        migrations.AlterField(
            model_name='site',
            name='name',
            field=models.CharField(max_length=200, unique=True),
        ),
    ]
