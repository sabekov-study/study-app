# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-05-13 11:13
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0018_auto_20170512_1517'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='siteevaluation',
            options={'permissions': (('can_review', 'Can review site evaluations'),)},
        ),
    ]