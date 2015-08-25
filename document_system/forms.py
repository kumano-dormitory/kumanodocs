#-*- coding: utf-8 -*-
import django.forms as forms
from django.forms import ModelForm, CheckboxSelectMultiple, TextInput, Textarea, Form, HiddenInput
from document_system.models import Issue, IssueType, Meeting, Note, Block
import hashlib

class IssueForm(ModelForm):
    '''資料のフォーム'''
    def __init__(self,*args,**kwargs):
        super(IssueForm,self).__init__(*args,**kwargs)
        self.fields['vote_content'].required = False

    def clean(self):
        cleaned_data = super(IssueForm, self).clean()
        
        # 採決項目が無いのを弾く
        saiketsu = IssueType.objects.get(name="採決")
        issue_types = self.cleaned_data.get("issue_types")
        vote_content = self.cleaned_data.get("vote_content")

        if issue_types != None and saiketsu in issue_types and vote_content == "":
            self.add_error('vote_content',"議案の種類に「採決」が選択されているので、「採決項目」は必須です。")

        # hashed_password変数に入っている平文のパスワードをhashする
        if cleaned_data.get("hashed_password") != None:
            cleaned_data['hashed_password'] = hashlib.sha512(cleaned_data["hashed_password"].encode("utf-8")).hexdigest()
            
        return cleaned_data

    class Meta:
        model = Issue
        fields = ('meeting','issue_types','title','author','hashed_password','text','vote_content',)
        widgets = {
            'issue_types':CheckboxSelectMultiple(),
            'title':TextInput(),
            'author':TextInput(),
            'hashed_password':TextInput(),
            'text':Textarea(attrs={'rows':'30'}),
            'vote_content':Textarea(attrs={'rows':'5'})
        }

class NormalIssueForm(IssueForm):
    def __init__(self,*args,**kwargs):
        super(NormalIssueForm,self).__init__(*args,**kwargs)
        self.fields['meeting'].queryset = Meeting.normal_meeting_queryset()

    def clean(self):
        cleaned_data = super(NormalIssueForm,self).clean()

        if cleaned_data.get('meeting') in list(Meeting.normal_meeting_queryset()):
            return cleaned_data
        else:
            self.add_error('meeting',"普通資料としての締め切りを過ぎています")

class BringIssueForm(IssueForm):
    def __init__(self,*args,**kwargs):
        super(BringIssueForm,self).__init__(*args,**kwargs)
        self.fields['meeting'].queryset = Meeting.bring_meeting_queryset()
    
    def clean(self):
        cleaned_data = super(BringIssueForm,self).clean()

        if cleaned_data.get('meeting') in list(Meeting.bring_meeting_queryset()):
            return cleaned_data
        else:
            self.add_error('meeting',"持込資料としての締め切りを過ぎています")

class AppendIssueForm(IssueForm):
    def __init__(self,*args,**kwargs):
        super(AppendIssueForm,self).__init__(*args,**kwargs)
        self.fields['meeting'].queryset = Meeting.append_meeting_queryset()

    def clean(self):
        cleaned_data = super(AppendIssueForm,self).clean()

        if cleaned_data.get('meeting') in list(Meeting.append_meeting_queryset()):
            return cleaned_data
        else:
            self.add_error('meeting',"追加資料としての締め切りを過ぎています")

class EditIssueForm(NormalIssueForm):
    def __init__(self,*args,**kwargs):
        issue_id = kwargs['issue_id']
        del kwargs['issue_id']

        super(EditIssueForm,self).__init__(*args,**kwargs)
        self.fields['id'] = forms.IntegerField( widget=HiddenInput, initial=issue_id )

    def clean(self):
        cleaned_data = super(EditIssueForm,self).clean()
        if cleaned_data.get("hashed_password") == Issue.objects.get(id__exact=cleaned_data['id']).hashed_password:
            return cleaned_data
        else:
            self.add_error('hashed_password','パスワードが間違っています')

class PostNoteForm(Form):
    block = forms.IntegerField( widget=forms.HiddenInput )
    hashed_password = forms.CharField( label="パスワード" )
    
    def __init__(self,*args,**kwargs):
        super(PostNoteForm,self).__init__(*args,**kwargs)
        
        meeting = Meeting.posting_note_meeting_queryset().get()

        for issue in Issue.objects.filter(meeting__exact=meeting).order_by('issue_order'):
            self.fields['issue_' + str(issue.id)] = forms.CharField( widget=forms.Textarea ,label=issue.get_qualified_title(), required=False )

    def clean(self):
        cleaned_data = super(PostNoteForm,self).clean()

        if Note.objects.filter( block__exact=Block.objects.get(id__exact=cleaned_data.get("block")), issue__meeting__exact=Meeting.posting_note_meeting_queryset().get() ).exists():
            self.add_error(None, "既に議事録は投稿されています")

class EditNoteForm(Form):
    hashed_password = forms.CharField( label="パスワード" )

    def __init__(self,*args,**kwargs):
        block_id = kwargs['block_id']
        del kwargs['block_id']

        super(EditNoteForm,self).__init__(*args,**kwargs)
        
        self.fields['block'] = forms.IntegerField( widget=forms.HiddenInput, initial=block_id )

        meeting = Meeting.posting_note_meeting_queryset().get()

        for note in Note.objects.filter(issue__meeting__exact=meeting,block__id__exact=block_id):
            self.fields['note_'+str(note.id)] = forms.CharField( widget=forms.Textarea, label=note.issue.title, required=False ,initial=note.text)
    
    def clean(self):
        cleaned_data = super(EditNoteForm,self).clean()
        
        meeting = Meeting.posting_note_meeting_queryset().get()
        issue   = Issue.objects.filter(meeting__exact=meeting).first()
        if cleaned_data.get('hashed_password') != None and hashlib.sha512( cleaned_data.get('hashed_password').encode('utf-8') ).hexdigest() == Note.objects.get(block__id__exact=cleaned_data.get('block'),issue__exact=issue).hashed_password:
            return cleaned_data
        else:
            self.add_error('hashed_password',"パスワードが間違っています")