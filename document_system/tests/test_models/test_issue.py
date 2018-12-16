# -*- coding: utf-8 -*-

from nose.tools import with_setup, raises
from document_system.models import Meeting, Issue, IssueType
from django.test import TestCase
from django_dynamic_fixture import G

from datetime import date, time, datetime, timedelta
import pytz

class TestIssue(TestCase):
    def setUp(self):
        IssueType(name="周知").save()

    def test_posting_table_issues(self):
        assert len(Issue.posting_table_issues()) == 0
        m = Meeting(meeting_date=date.today() + timedelta(weeks=4))
        m.save()
        i = Issue(meeting=m, title='Title', author="Author", text="Text", hashed_password="hashed_password")
        i.save()
        i.issue_types.add(IssueType.objects.all()[0])
        assert len(Issue.posting_table_issues()) == 1
