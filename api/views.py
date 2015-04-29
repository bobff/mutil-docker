#coding=utf-8
import re
import simplejson
import struct,socket
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect, HttpResponse
from django.db.models import Min,Max,Sum 
from dockers.views.client import Client
from django.views.decorators.http import require_http_methods
from dockers.models import Container
from network.models import IPv4Pool
from .decorators import protected_resource
import hashlib
from django.conf import settings
import random
from .models import User, CreatePermission
import datetime
from django.core.cache import cache

def set_token_cache(token, user):
    # request.session[validate_code] = user
    # request.session.set_expiry(settings.API_TIME_OUT)
    return cache.set(token, user, 60)

def get_token_cache(token):
    return cache.get(token)

@require_http_methods(['POST'])
def get_token(request):
    user = request.POST.get('user')
    passwd = request.POST.get('passwd')
    try:
        uobj = User.objects.get(name=user, password=passwd, active=True)
        if uobj.ipv4 != None and uobj.ipv4 != '':
            if uobj.ipv4 != request.META['REMOTE_ADDR']:
                return HttpResponse(simplejson.dumps({'res':False, 'err': 'Request from a wrong IP address'}), mimetype = 'application/json')
    except:
        return HttpResponse(simplejson.dumps({'res':False, 'err': 'Validate failed'}), mimetype = 'application/json')
    
    md5 = hashlib.md5()
    md5.update(uobj.name + uobj.password)
    md5.update(str(random.random()))
    validate_code = md5.hexdigest()  
    
    set_token_cache(validate_code, user)
    return HttpResponse(simplejson.dumps({'res': True, 'token': validate_code}), mimetype = 'application/json')


########################### container start ##############################################
# @add_log()
@require_http_methods(['GET'])
@protected_resource()
def get_containers(request, *args, **kwargs):
    pre = request.GET.get('pre', None)
    client      = Client()
    obj_list    = client.get_containers()
    if pre != None and pre != '':
        pre = '/' + pre.split('/')[-1]
        tmp_list = []
        for obj in obj_list:
            for name in obj['Names']:
                if re.match(pre, name) != None:
                    obj['Names'] = [name]
                    tmp_list.append(obj)
        obj_list = tmp_list
    new_list = []
    for obj in obj_list:
        obj['Login_name'] = obj['info'].login_name
        obj['Login_pwd']  = obj['info'].login_pwd
        obj['Disk_limit'] = obj['info'].disk_limit
        obj['Cpu_share']  = obj['info'].cpu_share
        obj['Network_ipv4'] = obj['info'].network_ipv4
        obj['Swap_limit'] = obj['info'].swap_limit
        del(obj['info'])
        new_list.append(obj)
    return HttpResponse(simplejson.dumps({'res':True, 'info':new_list}), mimetype = 'application/json')

@require_http_methods(['GET'])
@protected_resource()
def get_container(request, *args, **kwargs):
    id = request.GET.get('id', None)
    if id != None and id != '':
        client = Client()
        obj_list = client.get_containers()
        o = None
        for obj in obj_list:
            if obj['Id'] == id:
                o = obj
                break
        if o == None:
            dicts = {'res': False, 'err': '未找到相应容器'}
        else:
            o['Login_name'] = o['info'].login_name
            o['Login_pwd']  = o['info'].login_pwd
            o['Disk_limit'] = o['info'].disk_limit
            o['Cpu_share']  = o['info'].cpu_share
            o['Network_ipv4'] = o['info'].network_ipv4
            o['Swap_limit'] = o['info'].swap_limit
            del(o['info'])
        dicts = {'res': True, 'info':o}
    else:
        dicts = {'res': False, 'err': 'id 参数错误'}
    return HttpResponse(simplejson.dumps(dicts), mimetype = 'application/json')

# @add_log()
@require_http_methods(['POST'])
@protected_resource()
def create_container(request, *args, **kwargs):
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
    ipv4pool    = request.POST.get('ipv4pool', '')
    name        = request.POST.get('name', '')
            
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
        'ipv4pool'  : ipv4pool,
        'name'      : name,
    }

    client = Client(hostname)
    c = client.create_container(data)
    return HttpResponse({'res':True, 'data':c.id})

@require_http_methods(['POST'])
@protected_resource()
def auto_create_container(request, *args, **kwargs):
    
    num  = request.POST.get('num', None)
    end_date = request.POST.get('end_date', None)
    image = request.POST.get('image', None)

    cpu  = request.POST.get('cpu', '')
    mem  = request.POST.get('mem', '')
    disk = request.POST.get('disk', '')
    port = request.POST.get('port', '')
    volume = request.POST.get('volume', '')

    valid = True

    try:
        num = int(num)
    except:
        pass
    
    if valid and end_date != None and validate_date(end_date) == False:
        valid = False
        dicts = {'res': False, 'err': 'end_date 日期格式错误， 正确格式： yyyy-mm-dd'}

    if valid and num <= 0:
        dicts = {'res':False, 'err': 'num参数无效'}
        valid = False
    if valid:
        pem = CreatePermission.objects.filter(user = request.api_user)
        if not pem.exists():
            dicts = {'res':False, 'err': '没有创建权限'}
            valid = False
        pem = pem[0]

    if valid:
        if not image:
            image = pem.image
        client = Client(pem.host.name)
        image_exist = False
        for i in client.get_images():
            if i['repotag'] == image:
                image = i['regrepotag']
                image_exist = True
                break
        if not image_exist:
            dicts = {'res':False, 'err': '镜像名有误'}
            valid = False
    if valid and num > pem.num:
        dicts = {'res':False, 'err': '超出创建容器数量限制'}
        valid = False

    if valid and num > (pem.pool.ip_count - pem.pool.ip_used_count):
        dicts = {'res':False, 'err': 'ip地址不够'}
        valid = False

    if valid:
        created = []
        for ip in pem.pool.get_free_ip_range(num):
            data = {
                'ip'        : ip, 
                'ip_size'   : pem.pool.size, 
                'port'      : port, 
                'image'     : image,
                'hostname'  : pem.host.name,
                'cmd'       : '',
                'cpu'       : cpu,
                'mem'       : mem,
                'swap'      : '',
                'disk'      : disk,
                'volume'    : volume,
                'ipv4pool'  : pem.pool.pk,
                'name'      : pem.user.name,
                'end_date'  : end_date,
            }
            # client = Client(pem.host.name)
            res, c = client.create_container(data)
            if res:
                info = {
                    'id'        : c.id,
                    'name'      : c.name,
                    'ipv4'      : c.network_ipv4,
                    'login_name': c.login_name,
                    'login_pwd' : c.login_pwd,
                    'cpu_share' : c.cpu_share,
                    'mem_limit' : c.mem_limit,
                    'swap_limit': c.swap_limit,
                    'disk_limit': c.disk_limit,
                    'port_bind' : c.port_bind,
                    'volume_bind': c.volume_bind,
                    'start_date': str(c.start_date),
                    'end_date'  : str(c.end_date),
                }
            created.append(res and {'res':res, 'info':info} or {'res':res, 'err':c})
        dicts = {'res': True, 'info': created}

    return HttpResponse(simplejson.dumps(dicts), mimetype = 'application/json')

def validate_date(date):
    try:
        tmp = date.split('-')
        datetime.date(int(tmp[0]), int(tmp[1]), int(tmp[2]))
    except:
        return False
    return True

@require_http_methods(['POST'])
@protected_resource()
def reset_end_date(request, *args, **kwargs):
    id = request.POST.get('id', None)
    end_date = request.POST.get('end_date', None)
    going = True
    if not id or not end_date:
        dicts = {'res': False, 'err': '参数错误'}
        going = False
    if going and validate_date(end_date) == False:
        going = False
        dicts = {'res': False, 'err': '参数错误，日期格式错误'}

    if going:
        try:
            container = Container.objects.get(id = id)
        except:
            going = False
            dicts = {'res': False, 'err': '未找到相应容器'}
    if going:
        container.end_date = end_date
        try:
            container.save()
            info = {
                    'id'        : container.id,
                    'name'      : container.name,
                    'ipv4'      : container.network_ipv4,
                    'login_name': container.login_name,
                    'login_pwd' : container.login_pwd,
                    'cpu_share' : container.cpu_share,
                    'mem_limit' : container.mem_limit,
                    'swap_limit': container.swap_limit,
                    'disk_limit': container.disk_limit,
                    'port_bind' : container.port_bind,
                    'volume_bind': container.volume_bind,
                    'start_date': str(container.start_date),
                    'end_date'  : str(container.end_date),
                }
            dicts = {'res': True, 'info': info}
        except:
            dicts = {'res': False, 'err': '设置失败'}
    return HttpResponse(simplejson.dumps(dicts))

# @add_log()
# @protected_resource()
# def get_ipv4pool(request, *args, **kwargs):
#     pools = IPv4Pool.objects.all()
#     res = []
#     for pool in pools:
#         res.append({'name': str(pool.net) + '/' + str(pool.size), 'ips': pool.get_free_ip_range()})
#     return HttpResponse({'res':True, 'data':res})

# @add_log()
# @protected_resource()
# def remove_container(request, *args, **kwargs):
#     id       = request.POST.get('id', False)
#     hostname = request.POST.get('host', False)
#     if id and hostname:
#         client = Client(hostname)
#         if client.remove_container(id):
#             return HttpResponse({'res': True, 'data': ''})
#     return HttpResponse({'res': False, 'error': '参数错误'})

# @add_log()
# @protected_resource()
# def start_container(request, *args, **kwargs):
#     id       = request.POST.get('id', False)
#     hostname = request.POST.get('host', False)
#     if id and hostname:
#         client = Client(hostname)
#         if client.start_container(id):
#             return HttpResponse({'res': True, 'data': ''})
#     return HttpResponse({'res': False, 'error': '参数错误'})

# @add_log()
# @protected_resource()
# def stop_container(request, *args, **kwargs):
#     id       = request.POST.get('id', False)
#     hostname = request.POST.get('host', False)
#     if id and hostname:
#         client = Client(hostname)
#         if client.stop_container(id):
#             return HttpResponse({'res':True, 'data':''})
#     return HttpResponse({'res':False, 'error':'参数错误'})

# @add_log()
# @protected_resource()
# def inspect(request, *args, **kwargs):
#     id       = request.GET.get('id')
#     hostname = request.GET.get('host')
#     if not id or not hostname:
#         return HttpResponse({'res':False, 'error':'参数错误'})
#     client  = Client(hostname)
#     obj     = client.inspect_container(id)
#     return HttpResponse({'res':True, 'data':obj})


# ################################ container end ####################################

# ################################ image start #####################################
# @add_log()
# @protected_resource()
# def get_images(request, *args, **kwargs):
#     hostname    = request.GET.get('host')
#     client      = Client(hostname)
#     data        = client.get_images()
#     return HttpResponse({'res':True, 'data':data})


# ################################ image end #########################################
