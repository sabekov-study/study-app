"""sabekov URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.shortcuts import redirect
from django.urls import include, path, re_path
from django.views.i18n import JavaScriptCatalog

import survey.urls

urlpatterns = [
    path('', lambda request: redirect('survey:index'), name='index'),
    path('survey/', include('survey.urls')),
    path('admin/', admin.site.urls),
    path('accounts/', include('account.urls')),
    path('base/', include('base.urls')),
    re_path(r'^i18n.js$', JavaScriptCatalog.as_view(), name='javascript-catalog'),
]
