# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-05-03 19:24
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0010_auto_20170503_1711'),
    ]

    operations = [
        migrations.AlterField(
            model_name='answerchoice',
            name='value',
            field=models.CharField(blank=True, default='', max_length=200),
        ),
    ]