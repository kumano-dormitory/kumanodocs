# -*- coding:utf-8 -*-
from django.conf.urls import patterns, url
from document_system import views
from django.views.generic import TemplateView

urlpatterns = patterns('',
    url(r'^$', views.top, name='top'),

    url(r'^post_issue/normal$', views.NormalIssueView.as_view(), name='post_normal_issue'),
    url(r'^post_issue/append$', views.AppendIssueView.as_view(), name='post_append_issue'),
    url(r'^edit_issue/(?P<issue_id>\d+)/$',views.edit_issue, name='edit_issue'),
    url(r'^delete_issue/(?P<issue_id>\d+)/$',views.delete_issue, name='delete_issue'),
    
    url(r'^post_note/(?P<block_id>\d+)/$', views.post_note, name='post_note'), 

    url(r'^browse_document/$', views.BrowseDocumentListView.as_view(), name='browse_document_list'),
    url(r'^browse_document/(?P<pk>\d+)/$', views.BrowseDocumentView.as_view(), name='browse_document'),
    
    url(r'^browse_issue/$', views.BrowseIssueListView.as_view() , name='browse_issue_list'),
    url(r'^browse_issue/(?P<pk>\d+)/$', views.BrowseIssueDetailView.as_view(), name='browse_issue_detail'),
    url(r'^browse_issue/(?P<pk>\d+)/pdf$', views.issue_pdf, name='browse_issue_detail_pdf'),

    url(r'^search_issue/$', views.SearchIssueListView.as_view(), name='search_issue'),
    
    url(r'^edit_note/(?P<block_id>\d+)/$',views.edit_note  , name='edit_note'),
    
    url(r'^post_table/(?P<issue_id>\d+)/$', views.PostTableView.as_view(), name='post_table'),
    url(r'^edit_table/(?P<pk>\d+)/$', views.EditTableView.as_view(), name='edit_table'),
    
    url(r'^download/$',TemplateView.as_view(template_name='document_system/download_page.html'), name='download_page'),

    url(r'^download/document/$',views.DownloadDocumentListView.as_view() , name='download_document_list'),
    url(r'^download/document/document/(?P<meeting_id>\d+)/$',views.download_document_detail,  name='download_document_detail'),
    url(r'^download/document/get_document/(?P<meeting_id>\d+)/$',views.document_pdf, name='get_pdf'),

    url(r'^download/note/get_note/$',views.DownloadNoteListView.as_view(), name='download_note_list'),
    url(r'^download/note/get_note/(?P<meeting_id>\d+)/$',views.note_pdf, name='get_note_pdf'),
)
