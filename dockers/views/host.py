#coding=utf-8
from django.shortcuts import render
from django.shortcuts import render_to_response
from django.template import RequestContext
from dockers.models import *
from django.db.models import Min,Max,Sum 
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
import docker 
import simplejson
from django.conf import settings
import struct,socket
from dockers.views import *
from dockers import *
from .client import Client

# Create your views here.

template_dir = 'host/'

@login_required
def list(request):
    '''hosts'''
    obj_list = Host.objects.all()
    for h in obj_list:
        print h.name, h.ipv4
        client = Client(h.name)
        try:
            res = client.ping()
        except:
            res = False
        if res =='OK':
            version = client.version()
            h.docker_v = version['Version']
            h.api_v = version['ApiVersion']
            h.kernel = version['KernelVersion']
            h.status = '01'
            info = client.info()
            h.info = info
        else:
            h.status = '10'
        h.save()
   
    return render_to_response(template_dir + 'list.html', {'obj_list':obj_list}, context_instance=RequestContext(request))
