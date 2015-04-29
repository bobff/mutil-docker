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
import os, uuid
import pycurl
import StringIO

from .client import Client

# Create your views here.

template_dir = 'image/'


@login_required
def list(request):
    '''image列表'''
    client = Client()
    images = client.get_all_images()
    return render_to_response(template_dir + 'list.html', {'images':images}, context_instance=RequestContext(request))

@login_required
def inspect(request):
    '''image详细信息'''
    id       = request.GET.get('id')
    hostname = request.GET.get('host')
    if not id or not hostname:
        return render_to_response(template_dir + 'inspect.html', {'msg':'no image id or hostname'}, context_instance=RequestContext(request))
    client = Client(hostname)
    obj = client.inspect_image(id)
    # try:
    #     db_obj = Image.objects.get(code__startswith=obj['Id'][:12])
    #     obj['dbinfo'] = db_obj
    # except:
    #     pass
    return render_to_response(template_dir + 'inspect.html', {'obj':obj}, context_instance=RequestContext(request))

@login_required
def ajax_get_images(request):
    hostname = request.GET.get('host')
    client = Client(hostname)
    dicts = {'obj_list':client.get_images()}
    return HttpResponse(simplejson.dumps(dicts), content_type = 'application/json')

@login_required
def build(request):
    if request.method == 'POST':
        dockerfile  = request.POST.get('dockerfile')
        # hostname    = request.POST.get('hostname')
        tag         = request.POST.get('tag')
        supervisord = request.POST.get('supervisord')
        login_name  = request.POST.get('login_name')
        login_pwd   = request.POST.get('login_pwd')
        # print login_name, login_pwd
        if len(dockerfile) > 0:
            client = Client()
            uid = uuid.uuid4()
            client.build(dockerfile, tag, supervisord=supervisord, uid=uid, login_name=login_name, login_pwd=login_pwd)
            return HttpResponseRedirect('/docker/build_log?id=' + str(uid))
    dicts ={}
    hosts = Host.objects.filter(status='01')
    dicts['hosts'] = hosts

    return render_to_response(template_dir + 'build.html', dicts, context_instance=RequestContext(request))

@login_required
def build_log(request):
    uid = request.GET.get('id')
    if id:
        client = Client()
        try:
            f = open(client.get_file_path('dockerfile', uid) + '/build.log', 'r')
            res = f.read()
            f.close()
        except:
            res = 'no log'
        return render_to_response(template_dir + 'build_log.html', {'res':res}, context_instance=RequestContext(request))
    return HttpResponseRedirect('/docker/hub')

@login_required
def ajax_remove(request):
    if request.method != 'POST':
        return HttpResponse(simplejson.dumps({'msg':'not post'}), content_type = 'application/json')
    id       = request.POST.get('id')
    hostname = request.POST.get('host')
    if id and hostname:
        client = Client(hostname)
        res = client.remove_image(id)
        return HttpResponse(simplejson.dumps({'msg':res}), content_type = 'application/json')
    return HttpResponse(simplejson.dumps({'msg':'failed'}), content_type = 'application/json')

@login_required
def hub(request):
    if not hasattr(settings, 'DOCKER_HUB_HOST') or not hasattr(settings, 'DOCKER_HUB_PORT'):
        raise Exception('config error:  settings.DOCKER_HUB_HOST or settings.DOCKER_HUB_PORT missing')
    
    if 1== 1:
    # try:
        dicts = {}
        q = request.GET.get('q','')
        buf = StringIO.StringIO()
        url = 'http://' + str(settings.DOCKER_HUB_HOST) + ':' + str(settings.DOCKER_HUB_PORT) + '/v1/search?q=' + str(q)
        c = pycurl.Curl()
        c.setopt(c.URL, url)
        c.setopt(c.WRITEFUNCTION, buf.write)
        c.perform()
        res = buf.getvalue()
        res = simplejson.loads(res)
        # count = 0
        # results = []
        # for r in res['results']:
        #     images = Image.objects.filter(name=r['name'])
        #     r['tags'] = []
        #     for i in images:
        #         r['tags'].append(i.tag)
        #     # if not images:
        #     #     r['tags'].append('latest')
        #     results.append(r)
        #     count += 1
        dicts['res'] = {'query':res['query'], 'num_results': res['num_results'], 'results': res['results']}
        buf.close()
    # except:
    #     raise Exception('connect to hub error, try CMD \' docker run -d -p 5000:5000 registry\' to start registry service')
    return render_to_response(template_dir + 'hub.html', dicts, context_instance=RequestContext(request))

@login_required
def push_log(request):
    host = request.GET.get('host')
    id = request.GET.get('id')
    if id and host:
        client = Client()
        f = open(client.get_file_path('images_' + host, id) + '/push.log', 'r')
        res = f.read()
        f.close()
        return render_to_response(template_dir + 'push_log.html', {'res':res}, context_instance=RequestContext(request))
    return HttpResponseRedirect('/docker/images')

@login_required
def push(request):
    if request.method == 'POST':
        id = request.POST.get('id', None)
        host = request.POST.get('host', None)
        if not id or not host:
            return HttpResponseRedirect('/docker/images')
        client = Client(host)
        res = client.push(id)
        return HttpResponseRedirect('/docker/push_log?id=%s&host=%s' % (id, host))

    dicts = {}
    imageid = request.GET.get('id', None)
    hostname = request.GET.get('host', None)
    if not imageid or not hostname:
        return HttpResponseRedirect('/docker/images')
    dicts['id'] = imageid
    dicts['hostname'] = hostname
    client = Client(hostname)
    obj = client.inspect_image(imageid)
    dicts['obj'] = obj
    return render_to_response(template_dir + 'push.html', dicts, context_instance=RequestContext(request))

@login_required
def pull(request):
    if request.method == 'POST':
        image = request.POST.get('image', None)
        host  = request.POST.get('host', None)
        tag   = request.POST.get('tag', None)
        uid = uuid.uuid4()
        client = Client(host)
        client.pull(image, tag, uid)
        return HttpResponseRedirect('/docker/pull_log?host='+host+'&uuid='+str(uid))
    image = request.GET.get('image')
    dicts = {}
    dicts['hosts'] = Host.objects.filter(status='01')

    buf = StringIO.StringIO()
    url = str('http://%s:%s/v1/repositories/%s/tags' % (str(settings.DOCKER_HUB_HOST), str(settings.DOCKER_HUB_PORT), image))
    print url, type(url)
    c = pycurl.Curl()
    c.setopt(c.URL, url)
    c.setopt(c.WRITEFUNCTION, buf.write)
    c.perform()
    res = buf.getvalue()
    res = simplejson.loads(res)
    dicts['tags'] = res
    print res
    # dicts['hub_host'] = settings.DOCKER_HUB_HOST
    # dicts['hub_port'] = settings.DOCKER_HUB_PORT
    # image_info = Image.objects.filter(name=image)
    # tags = []
    # for info in image_info:
    #     tags.append(info.tag)
    # dicts['tags'] = tags

    return render_to_response(template_dir + 'pull.html', dicts, context_instance=RequestContext(request))


@login_required
def pull_log(request):
    host = request.GET.get('host')
    uid = request.GET.get('uuid')
    if uid and host:
        client = Client()
        f = open(client.get_file_path('images_' + host, uid) + '/pull.log', 'r')
        res = f.read()
        f.close()
        return render_to_response(template_dir + 'pull_log.html', {'res':res}, context_instance=RequestContext(request))
    return HttpResponseRedirect('/docker/images')