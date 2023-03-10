# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-05-07 17:54
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('survey', '0015_auto_20170506_1448'),
    ]

    operations = [
        migrations.CreateModel(
            name='HistoricalAnswerChoice',
            fields=[
                ('id', models.IntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('full_label', models.SlugField(max_length=100)),
                ('value', models.CharField(blank=True, default='', max_length=200)),
                ('note', models.CharField(blank=True, max_length=300)),
                ('discussion_needed', models.BooleanField(default=False)),
                ('revision_needed', models.BooleanField(default=False)),
                ('last_updated', models.DateTimeField(blank=True, editable=False)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField()),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('evaluation', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='survey.SiteEvaluation')),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('parent', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='survey.HistoricalAnswerChoice')),
                ('question', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='survey.Question')),
            ],
            options={
                'verbose_name': 'historical answer choice',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
            },
        ),
        migrations.CreateModel(
            name='HistoricalAnswerOption',
            fields=[
                ('id', models.IntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('negativ', models.BooleanField(default=False)),
                ('_order', models.IntegerField(editable=False)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField()),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('question', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='survey.Question')),
            ],
            options={
                'verbose_name': 'historical answer option',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
            },
        ),
        migrations.CreateModel(
            name='HistoricalQuestion',
            fields=[
                ('id', models.IntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('label', models.SlugField(max_length=30)),
                ('question_text', models.CharField(blank=True, max_length=200)),
                ('comment', models.CharField(blank=True, max_length=300)),
                ('answer_type', models.CharField(blank=True, choices=[('AL', 'Alternatives'), ('MU', 'Multiple nominations'), ('IN', 'Input')], default='AL', max_length=2)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField()),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('catalog', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='survey.Catalog')),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('reference', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='survey.Catalog')),
            ],
            options={
                'verbose_name': 'historical question',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
            },
        ),
        migrations.AlterModelOptions(
            name='site',
            options={'ordering': ['name']},
        ),
        migrations.AddField(
            model_name='answerchoice',
            name='last_updated',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
