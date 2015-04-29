#coding=utf-8
import docker 
import simplejson

from django.conf import settings
from django.http import HttpResponseRedirect
from dockers.models import Host

def index(request):
    return HttpResponseRedirect('/docker/containers')
