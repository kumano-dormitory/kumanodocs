# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

def forwards_func(apps,schema_editor):
    ''' すごく汚い実装だし遅いけど、早々実行する処理じゃないし気にしない '''
    Note = apps.get_model('document_system', 'Note')
    db_alias = schema_editor.connection.alias
    
    note = []
    for n in Note.objects.select_related('block', 'issue'):
        _notes = Note.objects.filter(block__exact=n.block, issue__exact=n.issue).order_by('-id')
        if _notes.count() > 1:
            note_not_to_delete = _notes.first()
            notes_to_delete = _notes.exclude(pk=note_not_to_delete.id).delete()

def reverse_func(apps,schema_editor):
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('document_system', '0005_auto_20160306_0435'),
    ]

    operations = [
        migrations.RunPython(
            forwards_func,
            reverse_func
        ),
    ]
