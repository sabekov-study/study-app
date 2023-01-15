from django.contrib.auth import views as auth_views
from django.urls import path, re_path

from . import views

urlpatterns = [
    re_path(r'^my$', views.my_account, name='my_account'),
    re_path(r'^change_password$', views.change_password, name='change_password'),
    path('login/', auth_views.LoginView, {
        'template_name': 'account/login.html',
        'extra_context': {'active_nav': 'login'}
    }, name='login'),
    path('logout/', auth_views.logout_then_login, name='logout'),
    path('password_reset/', auth_views.PasswordResetView, {
        'template_name': 'account/password_reset_form.html'
    }, name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView, {
        'template_name': 'account/password_reset_done.html'
    }, name='password_reset_done'),
    re_path(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        auth_views.PasswordResetConfirmView, {
        'template_name': 'account/password_reset_confirm.html'
    }, name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView, {
        'template_name': 'account/password_reset_complete.html'
    }, name='password_reset_complete'),
]
