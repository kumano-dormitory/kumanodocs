# -*- coding: utf-8 -*-
 
from nose.tools import with_setup, raises
from document_system.models import Meeting, Issue
from django.test import TestCase
from django_dynamic_fixture import G

from datetime import date, time, datetime, timedelta
import pytz

class TestMeeting(TestCase):
	def setUp(self):
		#today = datetime.date.today()
		#for i in range(1,5):
		#	G(Meeting)
		pass

	def test_is_migrated_from_old_system(self):
		meeting = G(Meeting, meeting_date=(date(year=2014, day=3, month=12)))

		assert meeting.is_migrated_from_old_system()

	def test_is_postable_normal_issue(self):
		meeting_yesterday = G(Meeting, meeting_date=(date.today() - timedelta(days=1)))
		assert not (meeting_yesterday.is_postable_normal_issue())

		meeting_today = G(Meeting, meeting_date=date.today())
		assert not (meeting_today.is_postable_normal_issue())

		meeting_three_days_after = G(Meeting, meeting_date=(date.today() + timedelta(days=3)))
		assert meeting_three_days_after.is_postable_normal_issue()

	def test_has_issue(self):
		meeting = G(Meeting)
		G(Issue, meeting=meeting)

		assert meeting.has_issue()

	def test_deadline_datetime(self):
		meeting = G(Meeting, meeting_date=date.today())
		deadline_date = date.today() - timedelta(days=2)
		deadline_time = time(hour=21, tzinfo=pytz.timezone('Asia/Tokyo'))
		deadline_datetime = datetime.combine(deadline_date, deadline_time)

		assert meeting.deadline_datetime() == deadline_datetime

	def test_previous_meeting(self):
		current_meeting = G(Meeting, meeting_date=date.today())
		previous_meeting = G(Meeting, meeting_date=(date.today() - timedelta(days=5)))

		assert current_meeting.previous_meeting() == previous_meeting