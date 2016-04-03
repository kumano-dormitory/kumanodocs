# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('document_system', '0006_delete_duplicate_record_from_notes'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='note',
            unique_together=set([('issue', 'block')]),
        ),
    ]
