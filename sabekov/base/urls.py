from django.conf.urls import url

from .views import test_page, imprint

app_name = 'base'
urlpatterns = [
    url(r'^test$', test_page, name='test_page'),
    url(r'^imprint$', imprint, name='imprint')
]