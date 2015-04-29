from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.conf import settings
admin.autodiscover()

from .views import *

urlpatterns = patterns('',
    # Examples:
    url(r'^get_containers$',    get_containers),
    url(r'^get_container$',    get_container),
    # url(r'^create_container$',  create_container),
    url(r'^auto_create_container$',  auto_create_container),
    url(r'^reset_end_date$', reset_end_date),
    # url(r'^get_ipv4pool$',      get_ipv4pool),
    # url(r'^blog/', include('blog.urls')),

   # url(r'^network', 'network'),
    
   url(r'^get_token$',      get_token),
    )



urlpatterns += patterns('api.tests',
    url(r'^create_container_test$', 'create_container_test'),
)

