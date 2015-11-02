# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.views.generic import ListView,DetailView
from django.views.generic.edit import FormView, UpdateView
from document_system.models import Meeting, Issue, Block, Note, IssueType, Table
from document_system.forms import NormalIssueForm,BringIssueForm,AppendIssueForm,EditIssueForm,PostNoteForm,EditNoteForm,TableForm,IssueOrderForm,SearchIssueForm

from django.template.loader import render_to_string
from django.http import HttpResponse

import hashlib

def top(request):
    return render_to_response('document_system/top.html',
                              {'Meeting':Meeting
                              ,'Block'  :Block},
                              context_instance=RequestContext(request))

class IssueView(FormView):
    template_name = 'document_system/post_issue.html'

    def get_context_data(self,**kwargs):
        context = super(IssueView,self).get_context_data(**kwargs)
        context['Meeting'] = Meeting
        context['Block']   = Block
        return context
    
    def form_valid(self, form):
        form.save()
        return redirect('document_system:top')

class NormalIssueView(IssueView):
    form_class    = NormalIssueForm

class BringIssueView(IssueView):
    form_class    = BringIssueForm

class AppendIssueView(IssueView):
    form_class    = AppendIssueForm

def edit_issue(request,issue_id=None):
    issue = Issue.objects.get(id__exact=issue_id)

    if not issue.meeting in list(Meeting.normal_meeting_queryset()):
        return redirect('document_system:top')
    
    if request.method == "POST":
        form = EditIssueForm(request.POST,instance=issue)
        if form.is_valid():
            form.save()
            return redirect('document_system:top')
    else:
        issue.hashed_password = ''
        form = EditIssueForm(instance=issue) 
    
    return render_to_response('document_system/post_issue.html',
                                {'Meeting':Meeting
                                ,'Block':Block
                                ,'form':form
                                },
                                context_instance=RequestContext(request))

class BrowseIssueListView(ListView):
    context_object_name = 'issue_list'
    template_name       = 'document_system/browse_issue_list.html'
    paginate_by         = 50
    queryset            = Issue.objects.order_by('-meeting__meeting_date','issue_order')

    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)
        context['Meeting'] = Meeting
        context['Block']   = Block
        return context

class BrowseIssueDetailView(DetailView):
    context_object_name = 'issue'
    template_name       = 'document_system/browse_issue_detail.html'
    model               = Issue
    
    def get_context_data(self,**kwargs):
        context = super(BrowseIssueDetailView,self).get_context_data(**kwargs)
        context['Meeting'] = Meeting
        context['Block']   = Block
        context['notes']   = [note for note in Note.objects.filter(issue__exact=context['issue']).order_by('block') if note.text != ""]
        return context

class SearchIssueListView(BrowseIssueListView):
    template_name = 'document_system/search_issue_list.html'
    
    def get_queryset(self):
        form = SearchIssueForm(self.request.GET)
        if form.is_valid():
            import re
            from django.db.models import Q
            queryset = Issue.objects.all()
            for keyword in re.split(r' |　',form.cleaned_data["keywords"]):
                queryset = queryset.filter(Q(title__icontains=keyword) | Q(author__icontains=keyword) | Q(text__icontains=keyword))
            return queryset

class EditIssueListView(ListView):
    meetings = Meeting.normal_meeting_queryset()

    context_object_name = 'issue_list'
    template_name       = 'document_system/edit_issue_list.html'
    pagenate_by         = 50
    queryset            = Issue.objects.filter(meeting__in=meetings)
    
    def get_context_data(self,**kwargs):
        context = super(EditIssueListView,self).get_context_data(**kwargs)
        context['Meeting'] = Meeting
        context['Block']   = Block
        return context

def post_note(request, block_id=None):
    if request.method == "POST":
        form = PostNoteForm(request.POST)
        if form.is_valid():
            block = Block.objects.get(id__exact=form.cleaned_data['block'])
            hashed_password = hashlib.sha512(form.cleaned_data['hashed_password'].encode("UTF-8")).hexdigest()
            
            for issue in Issue.objects.filter(meeting__exact=Meeting.posting_note_meeting_queryset().get()):
                note = Note()
                note.issue = issue
                note.block = block
                note.text  = form.cleaned_data['issue_' + str(issue.id)]
                note.hashed_password = hashed_password
                note.save()

            return redirect('document_system:top')
            
    else:
        form = PostNoteForm(initial={'block':int(block_id)})
    return render_to_response('document_system/post_note.html',
                                {'Meeting':Meeting
                                ,'Block':Block
                                ,'posting_block':Block.objects.get(id__exact=block_id)
                                ,'form':form
                                },
                                context_instance=RequestContext(request))


def edit_note(request, block_id=None):
    if request.method == "POST":
        form = EditNoteForm(request.POST,block_id=block_id)
        if form.is_valid():
            posting_block = Block.objects.get(id__exact=form.cleaned_data['block'])
            hashed_password = hashlib.sha512(form.cleaned_data['hashed_password'].encode("UTF-8")).hexdigest()
            
            for issue in Issue.objects.filter(meeting__exact=Meeting.posting_note_meeting_queryset().get()):
                note = Note.objects.get(issue__exact=issue,block__exact=posting_block)
                note.text = form.cleaned_data['note_' + str(note.id)]
                note.save()

            return redirect('document_system:top')
            
    else:
        form = EditNoteForm(block_id=block_id)

    return render_to_response('document_system/edit_note.html',
                                {'Meeting':Meeting
                                ,'Block':Block
                                ,'posting_block':Block.objects.get(id__exact=block_id)
                                ,'form':form
                                },
                                context_instance=RequestContext(request))

class PostTableView(FormView):
    template_name = 'document_system/post_table.html'
    form_class    = TableForm

    def get_context_data(self,**kwargs):
        context = super(PostTableView,self).get_context_data(**kwargs)
        context['Meeting'] = Meeting
        return context

    def form_valid(self, form):
        form.save()
        return redirect('document_system:top')

class EditTableView(UpdateView):
    model = Table
    template_name = 'document_system/edit_table.html'
    form_class    = TableForm

    def render_to_response(self,context, **response_kwargs):
        if not self.object.issue in Issue.posting_table_issue_queryset():
            return redirect('document_system:top')

        return super(EditTableView,self).render_to_response(context, **response_kwargs)
 
    def get_form_kwargs(self):
        kwargs = super(EditTableView,self).get_form_kwargs()
        table_object = kwargs['instance']
        table_object.csv_text=''
        kwargs['instance'] = table_object
        return kwargs

    def get_context_data(self,**kwargs):
        context = super(EditTableView,self).get_context_data(**kwargs)
        context['Meeting'] = Meeting
        return context

    def form_valid(self, form):
        form.save()
        return redirect('document_system:top')

class DownloadDocumentListView(ListView):
    context_object_name = 'meeting_list'
    template_name       = 'document_system/download_document_list.html'
    queryset            = Meeting.rearrange_issues_meeting_queryset()

    def get_context_data(self,**kwargs):
        context = super(DownloadDocumentListView,self).get_context_data(**kwargs)
        context['Meeting'] = Meeting
        context['Block']   = Block
        return context

class DownloadNoteListView(ListView):
    context_object_name = 'meeting_list'
    template_name = 'document_system/download_note_list.html'
    queryset      = Meeting.download_note_meeting_queryset()
    
    def get_context_data(self,**kwargs):
        context = super(DownloadNoteListView,self).get_context_data(**kwargs)
        context['Meeting'] = Meeting
        context['Block']   = Block
        return context

def download_document_detail(request, meeting_id=None):
    if request.method == 'POST':
        form = IssueOrderForm(request.POST,meeting_id=meeting_id)
        if form.is_valid():
            issues = Issue.objects.filter(meeting__id__exact=meeting_id)
            for issue in issues:
                issue.issue_order = form.cleaned_data['issue_'+str(issue.id)]
                issue.save()
            return redirect('document_system:get_pdf',meeting_id=meeting_id)
    else:
        form = IssueOrderForm(meeting_id=meeting_id)
    
    return render_to_response('document_system/download_document_detail.html',
                                {'Meeting':Meeting
                                ,'Block':Block
                                ,'issues':Issue.objects.filter(meeting__id__exact=meeting_id).order_by('issue_order')
                                ,'form':form
                                ,'meeting_id':meeting_id
                                },
                                context_instance=RequestContext(request))
    

def pdf_html(request, meeting_id=None):
    meeting = Meeting.objects.get(id__exact=meeting_id)
    issues  = Issue.objects.filter(meeting__exact=meeting).order_by('issue_order')
    prev_meeting = Meeting.objects.filter(meeting_date__lt=meeting.meeting_date).order_by('-meeting_date').first()
    prev_issues = [issue for issue in Issue.objects.filter(meeting__exact=prev_meeting).order_by('issue_order') if not all(map(lambda note: note.text == "", issue.notes()))]
    
    html_string = render_to_string(
        'document_system/pdf/main.tex',
        {'meeting':meeting,
         'issues' :issues,
         'previous_issues':prev_issues,},
        context_instance=RequestContext(request))
    
    with open("/tmp/kumanodocs_meeting." + str(meeting.id) + ".tex",'w') as f:
        f.write(html_string)

    import subprocess

    subprocess.check_call(["lualatex","kumanodocs_meeting." + str(meeting.id) + ".tex",],cwd='/tmp')
    subprocess.check_call(["lualatex","kumanodocs_meeting." + str(meeting.id) + ".tex",],cwd='/tmp')
    
    with open("/tmp/kumanodocs_meeting." + str(meeting.id) + ".pdf","rb") as f:
        response = HttpResponse(f.read(),content_type="application/pdf")
        response['Content-Disposition'] = 'attachment; filename="' + str(meeting.meeting_date) + '.pdf"'
        return response

def note_pdf(request, meeting_id=None):
    meeting = Meeting.objects.get(id__exact=meeting_id)
    issues = [issue for issue in Issue.objects.filter(meeting__exact=meeting).order_by('issue_order') if not all(map(lambda note: note.text == "", issue.notes()))]
    html_string = render_to_string(
        'document_system/pdf/note.tex',
        {'meeting':meeting,
         'issues' :issues,},
        context_instance=RequestContext(request))
    
    with open("/tmp/kumanodocs_meeting." + str(meeting.id) + "note.tex",'w') as f:
        f.write(html_string)

    import subprocess

    subprocess.check_call(["lualatex","kumanodocs_meeting." + str(meeting.id) + "note.tex",],cwd='/tmp')
    subprocess.check_call(["lualatex","kumanodocs_meeting." + str(meeting.id) + "note.tex",],cwd='/tmp')
    
    with open("/tmp/kumanodocs_meeting." + str(meeting.id) + "note.pdf","rb") as f:
        response = HttpResponse(f.read(),content_type="application/pdf")
        response['Content-Disposition'] = 'attachment; filename="' + str(meeting.meeting_date) + '(NOTE)' + '.pdf"'
        return response
