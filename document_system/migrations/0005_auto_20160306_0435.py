# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

class Migration(migrations.Migration):

    dependencies = [
        ('document_system', '0004_set_default_timestamp'),
    ]

    operations = [
        migrations.AlterField(
            model_name='issue',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='issue',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
