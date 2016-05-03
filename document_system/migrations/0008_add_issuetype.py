# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

def forwards_func(apps,schema_editor):
    IssueType = apps.get_model('document_system', 'IssueType')
    db_alias = schema_editor.connection.alias

    if not IssueType.objects.filter(name='採決予定').exists():
        issue_type = IssueType(name='採決予定')
        issue_type.save()

def reverse_func(apps,schema_editor):
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('document_system', '0007_auto_20160306_2044'),
    ]

    operations = [
        migrations.RunPython(
            forwards_func,
            reverse_func
        ),
    ]
