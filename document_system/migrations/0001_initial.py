# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Block',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('name', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Issue',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('title', models.TextField(verbose_name='タイトル')),
                ('author', models.TextField(verbose_name='文責者')),
                ('text', models.TextField(verbose_name='本文')),
                ('vote_content', models.TextField(verbose_name='採決内容', blank=True)),
                ('hashed_password', models.TextField(verbose_name='パスワード')),
                ('issue_order', models.IntegerField(verbose_name='議案の順番', default=-1)),
            ],
            options={
                'verbose_name_plural': 'ブロック会議の議案',
            },
        ),
        migrations.CreateModel(
            name='IssueType',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('name', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Meeting',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('meeting_date', models.DateField(verbose_name='日付')),
            ],
            options={
                'verbose_name_plural': 'ブロック会議の日程',
            },
        ),
        migrations.CreateModel(
            name='Note',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('text', models.TextField(blank=True)),
                ('hashed_password', models.TextField()),
                ('block', models.ForeignKey(verbose_name='ブロック', to='document_system.Block')),
                ('issue', models.ForeignKey(verbose_name='議案', to='document_system.Issue')),
            ],
            options={
                'verbose_name_plural': 'ブロック会議の議事録',
            },
        ),
        migrations.CreateModel(
            name='Table',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('caption', models.TextField(verbose_name='表のタイトル')),
                ('csv_text', models.TextField(verbose_name='表')),
                ('table_order', models.IntegerField(verbose_name='表の順番', default=-1)),
                ('issue', models.ForeignKey(verbose_name='議案', to='document_system.Issue')),
            ],
        ),
        migrations.AddField(
            model_name='issue',
            name='issue_types',
            field=models.ManyToManyField(to='document_system.IssueType', verbose_name='議案の種類'),
        ),
        migrations.AddField(
            model_name='issue',
            name='meeting',
            field=models.ForeignKey(verbose_name='日付', to='document_system.Meeting'),
        ),
    ]
