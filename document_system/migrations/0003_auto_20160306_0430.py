# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('document_system', '0002_auto_20160302_2359'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='issuetype',
            options={'verbose_name_plural': '議案の種類'},
        ),
        migrations.AddField(
            model_name='issue',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='issue',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
    ]
