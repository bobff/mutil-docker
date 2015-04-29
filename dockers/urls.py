from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.conf import settings
from django.http import HttpResponseRedirect
admin.autodiscover()

urlpatterns = patterns('dockers.views',
    # Examples:
    url(r'^$', 'index'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^containers$', 'container.list'),
    url(r'^attach$', 'container.attach'),
    url(r'^inspect_container$', 'container.inspect'),
    url(r'^create_container$', 'container.create'),
    url(r'^logs$', 'container.logs'),
    url(r'^commit$', 'container.commit'),
    url(r'^ajax_remove_container$', 'container.ajax_remove'),
    url(r'^ajax_stop_container$', 'container.ajax_stop'),
    url(r'^ajax_start_container$', 'container.ajax_start'),
    url(r'^ajax_pause_container$', 'container.ajax_pause'),

    url(r'^images$', 'image.list'),
    url(r'^ajax_remove_image$', 'image.ajax_remove'),
    url(r'^inspect_image$', 'image.inspect'),
    url(r'^ajax_get_images$', 'image.ajax_get_images'),
    url(r'^build_image$', 'image.build'),
    url(r'^build_log$', 'image.build_log'),
    url(r'^hub$', 'image.hub'),
    url(r'^push$', 'image.push'),
    url(r'^push_log$', 'image.push_log'),
    url(r'^pull$', 'image.pull'),
    url(r'^pull_log$', 'image.pull_log'),


    url(r'^hosts', 'host.list'),

   # url(r'^network', 'network'),
    

    )


