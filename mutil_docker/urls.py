from django.conf.urls import patterns, include, url
from django.conf import settings
from django.contrib import admin
from django.contrib.auth.views import login, logout

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'dockers.views.index'),

    url(r'^admin/',  include(admin.site.urls)),
    url(r'^docker/', include('dockers.urls')),
    url(r'^api/',    include('api.urls')),
    url(r'^network/',    include('network.urls')),

    url(r'^accounts/login/$',  login, {'template_name':'login.html'}), 
    url(r'^accounts/logout/$', logout),
)

urlpatterns += patterns('',
    url(r'^site_media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_PATH}),
    url(r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT}),
    # url(r'^o/', include('oauth2_provider.urls', namespace='oauth2_provider')),
)

