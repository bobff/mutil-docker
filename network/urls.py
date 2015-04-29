from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.conf import settings
from django.http import HttpResponseRedirect
admin.autodiscover()

urlpatterns = patterns('network.views',
    # Examples:
    url(r'^ajax_get_free_ip_range$', 'ajax_get_free_ip_range'),
    url(r'^ajax_register_ip$', 'ajax_register_ip'),
    # url(r'^blog/', include('blog.urls')),
    )
