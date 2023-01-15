from django.shortcuts import redirect
from django.urls import path, re_path

from .models import *
from . import views

app_name = 'survey'
urlpatterns = [
    path('', lambda request: redirect('survey:site_overview',
        Checklist.objects.filter(is_active=True).last().id), name='index'),
    re_path(r'^(?P<checklist_id>[0-9]+)/$', views.index, name='site_overview'),
    re_path(r'^(?P<checklist_id>[0-9]+)/(?P<site_id>[0-9]+)/$', views.evaluate, name='evaluate'),
    re_path(r'^(?P<checklist_id>[0-9]+)/summary/$', views.SummaryListView.as_view(), name='summary-list'),
    re_path(r'^(?P<checklist_id>[0-9]+)/summary-by-user/$',
        views.SummaryByUserListView.as_view(), name='summary-by-user-list'),
    re_path(r'^compare/(?P<checklist_id>[0-9]+)/(?P<site_id>[0-9]+)/$', views.CompareListView.as_view(), name='compare'),
    re_path(r'^(?P<checklist_id>[0-9]+)/export/$', views.export, name='export'),
    re_path(r'^discuss/(?P<checklist_id>[0-9]+)/(?P<user_id>[0-9]+)/$', views.DiscussionView.as_view(), name='discuss'),
    re_path(r'^review/(?P<eval_id>[0-9]+)/$', views.ReviewDetailView.as_view(), name='review'),
    re_path(r'^import/$', views.ImportChecklistView.as_view(), name='import-checklist'),
    re_path(r'^apply-import/(?P<checklist_id>[0-9]+)/$', views.apply_import, name='apply-import'),
    re_path(r'^ajax/clear-discussion/(?P<answerchoice_id>[0-9]+)/$', views.clear_discussion, name='clear-discussion'),
]
