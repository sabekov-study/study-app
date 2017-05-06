# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-05-05 09:15
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0012_auto_20170505_1038'),
    ]

    operations = [
        migrations.AlterField(
            model_name='catalog',
            name='label',
            field=models.SlugField(max_length=30),
        ),
        migrations.AlterUniqueTogether(
            name='catalog',
            unique_together=set([('checklist', 'label')]),
        ),
    ]