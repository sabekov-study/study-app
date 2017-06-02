from django.conf.urls import url
from django.shortcuts import redirect

from .models import *
from . import views

app_name = 'survey'
urlpatterns = [
    url(r'^$', lambda request: redirect('survey:site_overview',
        Checklist.objects.filter(is_active=True).last().id), name='index'),
    url(r'^(?P<checklist_id>[0-9]+)/$', views.index, name='site_overview'),
    url(r'^(?P<checklist_id>[0-9]+)/(?P<site_id>[0-9]+)/$', views.evaluate, name='evaluate'),
    url(r'^(?P<checklist_id>[0-9]+)/summary/$', views.SummaryListView.as_view(), name='summary-list'),
    url(r'^(?P<checklist_id>[0-9]+)/summary-by-user/$',
        views.SummaryByUserListView.as_view(), name='summary-by-user-list'),
    url(r'^compare/(?P<checklist_id>[0-9]+)/(?P<site_id>[0-9]+)/$', views.CompareListView.as_view(), name='compare'),
    url(r'^review/(?P<eval_id>[0-9]+)/$', views.ReviewDetailView.as_view(), name='review'),
    url(r'^import/$', views.ImportChecklistView.as_view(), name='import-checklist'),
    url(r'^apply-import/(?P<checklist_id>[0-9]+)/$', views.apply_import, name='apply-import'),
]
