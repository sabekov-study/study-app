from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^(?P<site_id>[0-9]+)/$', views.evaluate, name='evaluate'),
]
