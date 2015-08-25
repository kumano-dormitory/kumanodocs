# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.views.generic import ListView,DetailView
from django.views.generic.edit import FormView, UpdateView
from document_system.models import Meeting, Issue, Block, Note, IssueType
from document_system.forms import NormalIssueForm,BringIssueForm,AppendIssueForm,EditIssueForm,PostNoteForm,EditNoteForm
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
    if request.method == "POST":
        form = EditIssueForm(request.POST,issue_id=issue_id)
        if form.is_valid():
            form.save()
            return redirect('document_system:top')
    else:
        issue = Issue.objects.get(id__exact=issue_id)
        issue.hashed_password = ''
        form = EditIssueForm(instance=issue,issue_id=issue_id) 
    
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
        context = super(BrowseIssueListView,self).get_context_data(**kwargs)
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
        context['notes']   = Note.objects.filter(issue__exact=context['issue']).order_by('block')
        return context

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
        meeting = Meeting.posting_note_meeting_queryset().get()
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