# -*- coding:utf-8 -*-

from django.db import models
from django.utils import html
from datetime import date, datetime, time, timedelta
from django.db.models import Q
from django.template.loader import render_to_string
import csv
import pytz

class PdfGenerateMixin(object):
    def output_pdf(self, tex_string,identifier,document_type):
        filename = '.'.join(["kumanodocs_meeting",str(identifier), document_type])

        with open("/tmp/" + filename + ".tex",'w') as f:
            f.write(tex_string)

        import subprocess

        subprocess.check_output(['ptex2pdf', '-u', '-l', filename + '.tex'],cwd='/tmp')
        subprocess.check_output(['ptex2pdf', '-u', '-l', filename + '.tex'],cwd='/tmp')

        return open("/tmp/" + filename + ".pdf","rb")

class Meeting(models.Model, PdfGenerateMixin):
    '''ブロック会議'''
    meeting_date = models.DateField("日付")
    
    def __str__(self):
        return self.meeting_date.strftime('%Y-%m-%d')
    
    @classmethod
    def normal_issue_meetings(cls):
        _meetings = cls.objects.filter(meeting_date__gte=date.today()).order_by('meeting_date')
        return filter(lambda meeting: meeting.is_postable_normal_issue() ,_meetings)

    @classmethod
    def exists_normal_issue_meetings(cls):
        return bool(list(cls.normal_issue_meetings()))
    
    @classmethod
    def append_meeting_queryset(cls):
        if datetime.now().time() <= time(hour=12):
            return cls.objects.filter(meeting_date__exact=(date.today()))
        elif time(hour=12) < datetime.now().time() and datetime.now().time() <= time(hour=22):
            return cls.objects.filter(Q(meeting_date__exact=(date.today())) | Q(meeting_date__exact=(date.today() + timedelta(days=1))))
        elif time(hour=22) < datetime.now().time():
            return cls.objects.filter(meeting_date__exact=(date.today() + timedelta(days=1)))
        else :
            return cls.objects.none()
    
    @classmethod
    def exists_append(cls):
        return cls.append_meeting_queryset().exists()

    @classmethod 
    def posting_table_meeting_queryset(cls):
        return cls.normal_issue_meetings() or cls.append_meeting_queryset()

    @classmethod
    def posting_note_meeting_queryset(cls):
        if datetime.now().time() >= time(hour=18):
            return cls.objects.get(meeting_date__exact=(date.today()))
        elif datetime.now().time() <= time(hour=18):
            return cls.objects.get(meeting_date__exact=(date.today() - timedelta(days=1)))
        else:
            return cls.objects.none()
    
    @classmethod
    def rearrange_issues_meeting_queryset(cls):
        if datetime.now().time() < time(hour=12):
            return cls.objects.filter(meeting_date__gte=(date.today() + timedelta(days=1)))
        else :
            return cls.objects.filter(meeting_date__gte=(date.today() + timedelta(days=2)))

    @classmethod
    def download_note_meeting_queryset(cls):
        return cls.objects.filter(meeting_date__lte=(date.today() + timedelta(days=15)))
    
    def is_migrated_from_old_system(self):
        if self.meeting_date < date(year=2015,month=9,day=30):
            return True
        else:
            return False

    def is_postable_normal_issue(self):
        if self.deadline_datetime() > datetime.now(tz=pytz.timezone('Asia/Tokyo')):
            return True
        else:
            return False

    def has_issue(self):
        return self.issue_set.exists()

    def deadline_datetime(self):
        deadline_date = self.meeting_date - timedelta(days=2)
        deadline_time = time(hour=21, tzinfo=pytz.timezone('Asia/Tokyo'))
        deadline_datetime = datetime.combine(deadline_date, deadline_time)
        return deadline_datetime

    def previous_meeting(self):
        return Meeting.objects.filter(meeting_date__lt=self.meeting_date).order_by('-meeting_date').first()

    def to_pdf(self):
        tex_string = render_to_string(
            'document_system/pdf/main.tex',
            {'meeting':self,
             'issues' :self.issue_set.normal_issue(),
             'previous_issues':self.previous_meeting().issue_set.has_notes()})
        return self.output_pdf(tex_string, self.id, 'document')

    class Meta:
        verbose_name_plural = "ブロック会議の日程"
        ordering = ('-meeting_date',)

class IssueType(models.Model):
    '''議案の種類'''
    name = models.TextField()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "議案の種類"

class IssueQuerySet(models.QuerySet):
    def append_issue(self):
        return filter(lambda issue: issue.is_append_issue(), self)

    def normal_issue(self):
        return filter(lambda issue: issue.is_normal_issue(), self)

    def has_notes(self):
        return filter(lambda issue: issue.has_notes(), self.order_by('issue_order'))

class IssueManager(models.Manager):
    def get_queryset(self):
        return IssueQuerySet(self.model, using=self._db)
    
    def append_issue(self):
        return self.get_queryset().append_issue()

    def normal_issue(self):
        return self.get_queryset().normal_issue()

    def has_notes(self):
        return self.get_queryset().has_notes()

class Issue(models.Model):
    '''議案'''
    meeting         = models.ForeignKey(Meeting,verbose_name="日付")
    issue_types     = models.ManyToManyField(IssueType,verbose_name="議案の種類")
    title           = models.TextField(verbose_name="タイトル")
    author          = models.TextField(verbose_name="文責者")
    text            = models.TextField(verbose_name="本文")
    vote_content    = models.TextField(verbose_name="採決内容",blank=True)
    hashed_password = models.TextField(verbose_name="パスワード")
    issue_order     = models.IntegerField(verbose_name="議案の順番",default=(-1))
    created_at      = models.DateTimeField(auto_now_add=True, null=False)
    updated_at      = models.DateTimeField(auto_now=True, null=False)

    objects = IssueManager()
    
    @classmethod
    def posting_table_issue_queryset(cls):
        return cls.objects.filter(meeting__in = Meeting.posting_table_meeting_queryset())

    def save(self, *args, **kwargs):
        if not self.pk:
            issue_order_max = self.meeting.issue_set.aggregate(models.Max('issue_order'))['issue_order__max']
            if issue_order_max:
                self.issue_order = issue_order_max + 1
            else:
                self.issue_order = 1
        return super(Issue, self).save(*args, **kwargs)

    def __str__(self):
        return self.title

    def get_qualified_title(self):
        return "【%s】%s【%s】" % (self.issue_number(),  self.title,  self.issue_types_str())

    def get_qualified_title_for_note(self):
        return "【0 - %s】%s【%s】" % (self.issue_number(), self.title, self.issue_types_str())
    
    def get_title_with_types(self):
        return "%s【%s】" % (self.title, self.issue_types_str())

    def get_tag_eliminated_text(self):
        return html.strip_tags(self.text)
    
    def is_votable(self):
        return IssueType.objects.get(name__exact="採決") in self.issue_types.all() or \
               IssueType.objects.get(name__exact="採決予定") in self.issue_types.all()

    def is_editable(self):
        if datetime.now(tz=pytz.timezone('Asia/Tokyo')) < self.meeting.deadline_datetime():
            return True
        else:
            return False

    def is_append_issue(self):
        if self.created_at > self.meeting.deadline_datetime():
            return True
        else:
            return False
    
    def is_normal_issue(self):
        return not self.is_append_issue()

    def has_notes(self):
        '''
        どこかのブロックが空でない議事録を投稿していればTrue
        そうでなければFalse
        '''
        for note in self.notes():
            if note.text != '':
                return True
        return False

    def notes(self):
        return self.note_set.order_by('block__name')

    def tables(self):
        return self.table_set.all()#.order_by('table_order')
    
    def issue_types_str(self):
        return "・".join([t.name for t in self.issue_types.all()])

    def issue_number(self):
        if self.is_append_issue():
            issue_number = "追加議案"
        else:
            issue_number = str(self.issue_order)

        return issue_number
        
    class Meta:
        verbose_name_plural = "ブロック会議の議案"
        ordering = ('-meeting__meeting_date','issue_order')
    
class Block(models.Model):
    '''ブロック'''
    name = models.TextField()

    def __str__(self):
        return self.name

    @classmethod
    def all_blocks(cls):
        return cls.objects.all()
    
    @classmethod
    def blocks_posted_notes(cls):
        meeting = Meeting.posting_note_meeting_queryset()
        if meeting:
            issue   = meeting.issue_set.first()
            if issue == None:
                return []
            else:
                notes = issue.note_set.select_related('block')
                return [note.block for note in notes]
        else:
            return []

    @classmethod
    def exists_blocks_posted_notes(cls):
        if cls.blocks_posted_notes() == []:
            return False
        else:
            return True

class Note(models.Model):
    '''議事録'''
    issue           = models.ForeignKey(Issue,verbose_name="議案")
    block           = models.ForeignKey(Block,verbose_name="ブロック")
    text            = models.TextField(blank=True)
    hashed_password = models.TextField()

    @classmethod
    def exists_same_note(cls, block, meeting):
        return cls.objects.filter(block__exact=block, issue__meeting__exact=meeting).exists()

    def __str__(self):
        return self.block.name + " " + self.issue.title
    
    class Meta:
        verbose_name_plural = "ブロック会議の議事録"
        unique_together = ('issue','block')

class Table(models.Model):
    '''表'''
    issue           = models.ForeignKey(Issue,verbose_name="議案")
    caption         = models.TextField(verbose_name="表のタイトル")
    csv_text        = models.TextField(verbose_name="表")
    table_order     = models.IntegerField(verbose_name="表の順番",default=(-1))

    def __str__(self):
        return self.caption + "(議案:" + self.issue.title + ")"

    def get_list(self):
        return csv.reader(self.csv_text.split('\n'),delimiter = '\t')

    class Meta:
        verbose_name_plural = "表"
