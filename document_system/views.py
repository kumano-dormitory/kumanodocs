# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.template import RequestContext
from django.views.generic import ListView,DetailView,TemplateView
from django.views.generic.edit import FormView, UpdateView, CreateView
from document_system.models import Meeting, Issue, Block, Note, IssueType, Table
from document_system.forms import NormalIssueForm,AppendIssueForm,EditIssueForm,PostNoteForm,EditNoteForm,TableForm,IssueOrderForm,SearchIssueForm,DeleteIssueForm
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string
from django.http import HttpResponse

import hashlib

def top(request):
    return render_to_response('document_system/top.html',
                              {'Meeting': Meeting
                              ,'Block':Block
                              },
                              context_instance=RequestContext(request))

class IssueView(FormView):
    template_name = 'document_system/post_issue.html'
    
    def form_valid(self, form):
        issue = form.save()
        if self.request.POST.get('table_addition'):
            return redirect('document_system:post_table',issue_id=issue.id)
        return redirect('document_system:browse_issue_detail',pk=issue.id)

class NormalIssueView(IssueView):
    form_class    = NormalIssueForm

class AppendIssueView(IssueView):
    form_class    = AppendIssueForm

def edit_issue(request,issue_id=None):
    issue = Issue.objects.get(id__exact=issue_id)

    if not issue.is_editable():
        return redirect('document_system:browse_issue_detail',pk=issue.id)
    
    if request.method == "POST":
        form = EditIssueForm(request.POST,instance=issue)
        if form.is_valid():
            form.save()
            if request.POST.get('table_addition'):
                return redirect('document_system:post_table',issue_id=issue.id)
            return redirect('document_system:browse_issue_detail',pk=issue.id)
    else:
        issue.hashed_password = ''
        form = EditIssueForm(instance=issue) 
    
    return render_to_response('document_system/post_issue.html',
                                {'form':form
                                ,'tables':issue.tables
                                },
                                context_instance=RequestContext(request))

def delete_issue(request, issue_id=None):
    issue = Issue.objects.get(id__exact=issue_id)
    
    if not issue.is_editable():
        return redirect('document_system:browse_issue_detail',pk=issue.id)

    if request.method == "POST":
        form = DeleteIssueForm(request.POST)
        if form.is_valid():
            issue.delete()
            return redirect('document_system:top')
    else:
        form = DeleteIssueForm(issue_id=issue_id)

    return render_to_response('document_system/delete_issue_detail.html',
                                {'form':form
                                ,'issue':issue
                                },
                                context_instance=RequestContext(request))

class BrowseIssueListView(ListView):
    context_object_name = 'issue_list'
    template_name       = 'document_system/browse_issue_list.html'
    paginate_by         = 50
    queryset            = Issue.objects.order_by('-meeting__meeting_date','issue_order')

class BrowseIssueDetailView(DetailView):
    context_object_name = 'issue'
    template_name       = 'document_system/browse_issue_detail.html'
    model               = Issue
    
    def get_context_data(self,**kwargs):
        context = super(BrowseIssueDetailView,self).get_context_data(**kwargs)
        context['notes']   = [note for note in Note.objects.filter(issue__exact=context['issue']).order_by('block') if note.text != ""]
        return context

class BrowseDocumentListView(ListView):
    context_object_name = 'meeting_list'
    template_name       = 'document_system/browse_document_list.html'
    paginate_by         = 20
    queryset            = Meeting.objects.all()

class BrowseDocumentView(ListView):
    context_object_name = 'issue_list'
    template_name       = 'document_system/browse_document.html'
    paginate_by         = 10

    def get_queryset(self):
        meeting = get_object_or_404(Meeting, id__exact=self.kwargs['pk'])
        return meeting.issue_set.order_by('issue_order')
    
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

    def get_context_data(self,**kwargs):
        context = super(SearchIssueListView,self).get_context_data(**kwargs)
        context['search_keywords'] = self.request.GET['keywords']
        return context
    
def post_note(request, block_id=None):
    if request.method == "POST":
        form = PostNoteForm(request.POST)
        if form.is_valid():
            block = Block.objects.get(pk=form.cleaned_data['block'])
            hashed_password = hashlib.sha512(form.cleaned_data['hashed_password'].encode("UTF-8")).hexdigest()
            
            for issue in Meeting.posting_note_meeting_queryset().issue_set.all():
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
                                {'posting_block':Block.objects.get(pk=block_id)
                                ,'form':form
                                },
                                context_instance=RequestContext(request))


def edit_note(request, block_id=None):
    if request.method == "POST":
        form = EditNoteForm(request.POST,block_id=block_id)
        if form.is_valid():
            posting_block = Block.objects.get(pk=form.cleaned_data['block'])
            hashed_password = hashlib.sha512(form.cleaned_data['hashed_password'].encode("UTF-8")).hexdigest()
            
            for issue in Meeting.posting_note_meeting_queryset().issue_set.all():
                note = Note.objects.get(issue__exact=issue,block__exact=posting_block)
                note.text = form.cleaned_data['note_' + str(note.id)]
                note.save()

            return redirect('document_system:top')
            
    else:
        form = EditNoteForm(block_id=block_id)

    return render_to_response('document_system/edit_note.html',
                                {'posting_block':Block.objects.get(id__exact=block_id)
                                ,'form':form
                                },
                                context_instance=RequestContext(request))

class PostTableView(CreateView):
    model = Table
    template_name = 'document_system/post_table.html'
    form_class    = TableForm

    def get_initial(self):
        initial = super(PostTableView,self).get_initial()
        initial['issue']=Issue.objects.get(pk=self.kwargs['issue_id'])
        return initial

    def get_success_url(self):
        return reverse('document_system:browse_issue_detail',kwargs={"pk":self.object.issue.id})

class EditTableView(UpdateView):
    model = Table
    template_name = 'document_system/post_table.html'
    form_class    = TableForm

    def render_to_response(self,context, **response_kwargs):
        if not self.object.issue in Issue.posting_table_issue_queryset():
            return redirect('document_system:top')

        return super(EditTableView,self).render_to_response(context, **response_kwargs)

    def get_initial(self):
        initial = super(EditTableView,self).get_initial()
        initial['csv_text']=""
        return initial

    def get_success_url(self):
        return reverse('document_system:browse_issue_detail',kwargs={"pk":self.object.issue.id})

class DownloadDocumentListView(ListView):
    context_object_name = 'meeting_list'
    template_name       = 'document_system/download_document_list.html'
    queryset            = Meeting.rearrange_issues_meeting_queryset()

class DownloadNoteListView(ListView):
    context_object_name = 'meeting_list'
    template_name = 'document_system/download_note_list.html'
    queryset      = Meeting.download_note_meeting_queryset()
    
def download_document_detail(request, meeting_id=None):
    meeting = Meeting.objects.get(pk=meeting_id)
    if request.method == 'POST':
        form = IssueOrderForm(request.POST,meeting_id=meeting_id)
        if form.is_valid():
            issues = meeting.issue_set.all()
            for issue in issues:
                issue.issue_order = form.cleaned_data['issue_'+str(issue.id)]
                issue.save()
            return redirect('document_system:get_pdf',meeting_id=meeting_id)
    else:
        form = IssueOrderForm(meeting_id=meeting_id)
    
    return render_to_response('document_system/download_document_detail.html',
                                {'issues':meeting.issue_set.order_by('issue_order')
                                ,'form':form
                                ,'meeting_id':meeting_id
                                },
                                context_instance=RequestContext(request))

def output_pdf(request,tex_string,meeting_id,document_type):
    filename = '.'.join(["kumanodocs_meeting",meeting_id, document_type])
    
    with open("/tmp/" + filename + ".tex",'w') as f:
        f.write(tex_string)

    import subprocess
    
    try:
        subprocess.check_output(['ptex2pdf', '-u', '-l', filename + '.tex'],cwd='/tmp')
        subprocess.check_output(['ptex2pdf', '-u', '-l', filename + '.tex'],cwd='/tmp')
    except subprocess.CalledProcessError as e:
        return render_to_response('document_system/pdf_error.html',
                                    {'error_output':e.output
                                    },
                                    context_instance=RequestContext(request))
    
    with open("/tmp/" + filename + ".pdf","rb") as f:
        response = HttpResponse(f.read(),content_type="application/pdf")
        response['Content-Disposition'] = 'attachment; filename="' + filename + '.pdf"'
        return response


def document_pdf(request, meeting_id=None):
    meeting = Meeting.objects.get(id__exact=meeting_id)
    issues = meeting.issue_set.normal_issue()
    prev_meeting = meeting.previous_meeting()
    prev_issues = prev_meeting.issue_set.has_notes()
    
    tex_string = render_to_string(
        'document_system/pdf/main.tex',
        {'meeting':meeting,
         'issues' :issues,
         'previous_issues':prev_issues,},
        context_instance=RequestContext(request))
    
    return output_pdf(request,tex_string,meeting_id,"document")

def note_pdf(request, meeting_id=None):
    meeting = Meeting.objects.get(id__exact=meeting_id)
    issues = meeting.issue_set.has_notes()
    tex_string = render_to_string(
        'document_system/pdf/note.tex',
        {'meeting':meeting,
         'issues' :issues,},
        context_instance=RequestContext(request))
    
    return output_pdf(request,tex_string,meeting_id,"note")
