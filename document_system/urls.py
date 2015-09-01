# -*- coding:utf-8 -*-
from django.conf.urls import patterns, url
from document_system import views

urlpatterns = patterns('',
    url(r'^$', views.top, name='top'),

    url(r'^post_issue/normal$', views.NormalIssueView.as_view(), name='post_normal_issue'),
    url(r'^post_issue/bring$', views.BringIssueView.as_view(), name='post_bring_issue'),
    url(r'^post_issue/append$', views.AppendIssueView.as_view(), name='post_append_issue'),
    url(r'^edit_issue/$'  , views.EditIssueListView.as_view()   , name='edit_issue'),
    url(r'^edit_issue/(?P<issue_id>\d+)/$',views.edit_issue, name='edit_issue'),
    
    url(r'^post_note/(?P<block_id>\d+)/$', views.post_note, name='post_note'), 
    
    url(r'^browse_issue/$', views.BrowseIssueListView.as_view() , name='browse_issue_list'),
    url(r'^browse_issue/(?P<pk>\d+)/$', views.BrowseIssueDetailView.as_view(), name='browse_issue_detail'),
    
    url(r'^edit_note/(?P<block_id>\d+)/$',views.edit_note  , name='edit_note'),
    
    url(r'^download_document/$',views.DownloadDocumentListView.as_view() , name='download_document_list'),
    url(r'^download_document/(?P<meeting_id>\d+)/$',views.download_document_detail,  name='download_document_detail'),
    url(r'^download_document/get_document/(?P<meeting_id>\d+)/$',views.pdf_html, name='get_pdf'),
)
