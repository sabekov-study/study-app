from django.conf.urls import url

from . import views

app_name = 'survey'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^(?P<checklist_id>[0-9]+)/$', views.index, name='site_overview'),
    url(r'^(?P<checklist_id>[0-9]+)/(?P<site_id>[0-9]+)/$', views.evaluate, name='evaluate'),
]
