from django.conf.urls import url
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    url(r'^my$', views.my_account, name='my_account'),
    url(r'^change_password$', views.change_password, name='change_password'),
    url(r'^login/$', auth_views.login, {
        'template_name': 'account/login.html',
        'extra_context': {'active_nav': 'login'}
    }, name='login'),
    url(r'^logout/$', auth_views.logout_then_login, name='logout'),
    url(r'^password_reset/$', auth_views.password_reset, {
        'template_name': 'account/password_reset_form.html'
    }, name='password_reset'),
    url(r'^password_reset/done/$', auth_views.password_reset_done, {
        'template_name': 'account/password_reset_done.html'
    }, name='password_reset_done'),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        auth_views.password_reset_confirm, {
        'template_name': 'account/password_reset_confirm.html'
    }, name='password_reset_confirm'),
    url(r'^reset/done/$', auth_views.password_reset_complete, {
        'template_name': 'account/password_reset_complete.html'
    }, name='password_reset_complete'),
]