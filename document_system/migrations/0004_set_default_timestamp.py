# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

from datetime import datetime, time, timedelta
import pytz

def forwards_func(apps, schema_editor):
    ''' 
    タイムスタンプを導出/設定
    議案番号が-1なら、締め切り後に設定
    議案番号が-1でないなら、締め切り前に設定
    '''
    Issue = apps.get_model('document_system', 'Issue')
    db_alias = schema_editor.connection.alias

    issues_null_timestamp = Issue.objects.using(db_alias).filter(models.Q(updated_at__exact=None) | models.Q(updated_at__exact=None))
    for issue in issues_null_timestamp:
        posted_date = issue.meeting.meeting_date - timedelta(days=2)
        if issue.issue_order < 0:
            posted_hour = time(hour=22, tzinfo=pytz.timezone('Asia/Tokyo'))
        else:
            posted_hour = time(hour=20, tzinfo=pytz.timezone('Asia/Tokyo'))
        timestamp = datetime.combine(posted_date, posted_hour)

        # updated_atの自動更新を無効にしないと、migrateした日時になってしまう
       	for field in issue._meta.local_fields:
    	    if field.name == "updated_at":
                field.auto_now = False

        issue.updated_at = timestamp
        issue.created_at = timestamp
        issue.save()

def reverse_func(apps, schema_editor):
    '''
    「forwards_funcで設定されたタイムスタンプ」だけを
    NULLにするのは難しいので、何もしない。
    '''
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('document_system', '0003_auto_20160306_0430'),
    ]

    operations = [
        migrations.RunPython(
            forwards_func, 
            reverse_func
        ),
    ]
