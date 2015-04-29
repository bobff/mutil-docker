#coding=utf-8
import os
from django.shortcuts import render
from django.shortcuts import render_to_response
from django.template import RequestContext
from dockers.models import *
from django.db.models import Min,Max,Sum 
from django.http import HttpResponseRedirect, HttpResponse
import docker 
import simplejson
from django.conf import settings
import struct,socket
from dockers.views import *
from django.contrib.auth.decorators import login_required

from .client import Client
from network.models import IPv4Pool
from ..models import Container

# Create your views here.

template_dir = 'container/'


@login_required
def list(request):
    '''container列表'''
    client = Client()
    obj_list = client.get_containers(all=True)
    return render_to_response(template_dir + 'list.html', {'obj_list':obj_list}, context_instance=RequestContext(request))

@login_required
def inspect(request):
    '''container详细信息'''
    id = request.GET.get('id')
    hostname = request.GET.get('host')
    if not id or not hostname:
        return render_to_response(template_dir + 'inspect.html', {'msg':'no container id or hostname'}, context_instance=RequestContext(request))

    client = Client(hostname)

    obj = client.inspect_container(id)
    # print obj
    try:
        dbinfo = Container.objects.get(id=id)
    except:
        dbinfo = None
    return render_to_response(template_dir + 'inspect.html', {'obj':obj, 'dbinfo':dbinfo}, context_instance=RequestContext(request))

# ipv4数字地址 
def ipv4_to_string(ipv4):
    ipv4_n = socket.htonl(ipv4)
    data = struct.pack('I', ipv4_n)
    ipv4_string = socket.inet_ntop(socket.AF_INET, data)
    return ipv4_string
def ipv4_from_string(ipv4_string):
    data = socket.inet_pton(socket.AF_INET, ipv4_string)
    ipv4_n = struct.unpack('I', data)
    ipv4 = socket.ntohl(ipv4_n[0])
    return ipv4

@login_required
def attach(request):
    id = request.GET.get('id')
    hostname = request.GET.get('host')
    if not id or not hostname:
        return render_to_response(template_dir + 'inspect.html', {'msg':'no container id or hostname'}, context_instance=RequestContext(request))
    cmd = 'sudo docker --tls -H='+hostname+':2376 attach --sig-proxy=false  ' + id
    print cmd
    print os.system(cmd)
    print os.system('\n')#################
    here
    return render_to_response(template_dir + 'inspect.html', {'msg':'no container id or hostname'}, context_instance=RequestContext(request))


@login_required
def create(request):
    '''创建新的container'''
    
    hosts = Host.objects.filter(status='01')
    dicts = {'hosts': hosts}
    ippools = IPv4Pool.objects.all()

    dicts['pools'] = ippools
    dicts['defaultuser'] = settings.DOCKER_DEFAULT_USER
    if request.method == 'GET':
        return render_to_response(template_dir + 'create.html', dicts, context_instance=RequestContext(request))

    ip          = request.POST.get('ip', '')
    port        = request.POST.get('port', '')
    image       = request.POST.get('image')
    hostname    = request.POST.get('hostname')
    cmd         = request.POST.get('cmd')
    cpu         = request.POST.get('cpu', '')
    mem         = request.POST.get('mem', '')
    swap        = request.POST.get('swap', '')
    disk        = request.POST.get('disk', '')
    volume      = request.POST.get('volume', '')
    name        = request.POST.get('name', None)
    pool        = request.POST.get('ipv4pool', '')
    passwd      = request.POST.get('passwd', '')

    if not ip:
        ip = ''
    ips = ip.split('/')
    ip = ips[0]
    if len(ips) > 1:
        ip_size = ips[1]
    else:
        ip_size = 24

    data = {
            'ip'        : ip, 
            'ip_size'   : ip_size, 
            'port'      : port, 
            'image'     : image,
            'hostname'  : hostname,
            'cmd'       : cmd,
            'cpu'       : cpu,
            'mem'       : mem,
            'swap'      : swap,
            'disk'      : disk,
            'volume'    : volume,
            'ipv4pool'  : pool,
            'name'      : name,
            'passwd'    : passwd,
        }

    if ip == '' or image == '' or hostname == '' or name == '' or pool == '':
        res = False
        c = '必填项不能为空'
    else:
        client = Client(hostname)
        res, c = client.create_container(data)

    if not res:
        dicts['data'] = data
        dicts['result'] = c
        return render_to_response(template_dir + 'create.html', dicts, context_instance=RequestContext(request))
    return HttpResponseRedirect('/docker/inspect_container?id=' + c.id + '&host=' + c.host_id)

@login_required
def ajax_remove(request):
    if request.method == 'POST':
        id       = request.POST.get('id', False)
        hostname = request.POST.get('host', False)
        if id and hostname:
            client = Client(hostname)
            if client.remove_container(id):
                return HttpResponse(simplejson.dumps({'res':True}), content_type = 'application/json')
    return HttpResponse(simplejson.dumps({'res':False}), content_type = 'application/json')

@login_required
def ajax_start(request):
    if request.method == 'POST':
        id       = request.POST.get('id', False)
        hostname = request.POST.get('host', False)
        if id and hostname:
            client = Client(hostname)
            if client.start_container(id):
                return HttpResponse(simplejson.dumps({'res':True}), content_type = 'application/json')
    return HttpResponse(simplejson.dumps({'res':False}), content_type = 'application/json')

@login_required
def ajax_pause(request):
    if request.method == 'POST':
        id       = request.POST.get('id', False)
        hostname = request.POST.get('host', False)
        if id and hostname:
            client = Client(hostname)
            if client.pause_container(id):
                return HttpResponse(simplejson.dumps({'res':True}), content_type = 'application/json')
    return HttpResponse(simplejson.dumps({'res':False}), content_type = 'application/json')

@login_required
def ajax_stop(request):
    if request.method == 'POST':
        id       = request.POST.get('id', False)
        hostname = request.POST.get('host', False)
        if id and hostname:
            client = Client(hostname)
            if client.stop_container(id):
                return HttpResponse(simplejson.dumps({'res':True}), content_type = 'application/json')
    return HttpResponse(simplejson.dumps({'res':False}), content_type = 'application/json')

@login_required
def logs(request):
    id       = request.GET.get('id')
    hostname = request.GET.get('host')
    client = Client(hostname)
    logs = client.logs(id)
    return render_to_response(template_dir + 'logs.html', {'logs':logs}, context_instance=RequestContext(request))

@login_required
def commit(request):
    if request.method == 'POST':
        id          = request.POST.get('id')
        hostname    = request.POST.get('hostname')
        repository  = request.POST.get('repository', None)
        tag         = request.POST.get('tag', None)
        author      = request.POST.get('author', None)
        message     = request.POST.get('message', None)
        if repository == '':
            repository = None
        if tag == '':
            tag = None
        if author == '':
            author = None
        if message == '':
            message = None
       
        client = Client(hostname)
       
        res = client.commit(id, 
            repository  = repository, 
            tag         = tag, 
            author      = author, 
            message     = message
            )
        #res = client.commit(id)
        # return HttpResponseRedirect('/docker/inspect_image?id='+res['Id']+'&host='+hostname)
        return HttpResponseRedirect('/docker/images')
    # id       = request.GET.get('id')
    # hostname = request.GET.get('host')
    # container = Container.objects.get(pk = id)
    # client = Client(hostname)
    # container = client.inspect_container(id)
    # image     = client.inspect_image(container['Image'])  
    image = request.GET.get('image')
    image = image.split(':')
    tag = image[-1]
    image = image[:-1]
    repo = ':'.join(image)
    dicts={ 'repo':repo, 'tag':tag}
    return render_to_response(template_dir + 'commit.html', dicts, context_instance=RequestContext(request))


from celery import Celery 
app = Celery()

@app.task(name='test')
def add(x,y):
    return x + y