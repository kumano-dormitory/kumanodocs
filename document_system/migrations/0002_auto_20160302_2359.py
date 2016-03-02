# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('document_system', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='issue',
            options={'verbose_name_plural': 'ブロック会議の議案', 'ordering': ('-meeting__meeting_date', 'issue_order')},
        ),
        migrations.AlterModelOptions(
            name='meeting',
            options={'verbose_name_plural': 'ブロック会議の日程', 'ordering': ('-meeting_date',)},
        ),
        migrations.AlterModelOptions(
            name='table',
            options={'verbose_name_plural': '表'},
        ),
    ]
