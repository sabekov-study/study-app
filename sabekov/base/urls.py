from django.urls import path

from .views import test_page, imprint

app_name = 'base'
urlpatterns = [
    path('test', test_page, name='test_page'),
    path('imprint', imprint, name='imprint')
]
