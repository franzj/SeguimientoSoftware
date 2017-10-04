from django.conf.urls import url, include
from .views import home, registrar

from django.conf.urls import url
from django.contrib.auth import views

urlpatterns = [
    url(r'^$', home, name='home'),
    url(r'^registrar/$', registrar, name='registrar'),
]
