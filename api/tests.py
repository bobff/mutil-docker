#coding=utf-8
import urllib,  urllib2
# from oauth2_provider.decorators import protected_resource

from django.views.decorators.csrf import csrf_exempt
from utils import render_to_response
from django.http import HttpResponseRedirect, HttpResponse

def get_access_token(code): 
    params = urllib.urlencode({
        'client_id': settings.OAUTH_CLIENT_ID ,
        'client_secret': settings.OAUTH_CLIENT_SECRET,
        'redirect_uri': settings.OAUTH_REDIRECT_URI,
        'grant_type' : 'authorization_code',
        'code' : code,
        })
    #定义一些文件头     
    headers = {"Content-Type":"application/x-www-form-urlencoded",     
               "Connection":"Keep-Alive","Referer":'http://nict.dcloud.cn/callback'}   
    #与网站构建一个连接     
    conn = httplib.HTTPConnection("open.csdb.cn")  
    #开始进行数据提交   同时也可以使用get进行     
    conn.request(method="POST",url="/oauth/access_token",body=params,headers=headers)     
    #返回处理后的数据     
    
    response = conn.getresponse() 
    if response.status != 200:
        return False
    res = response.read()
    conn.close()
    return simplejson.loads(res)


def get_container_test(request, *args, **kwargs):
    data = {
        'hostname': 'docker23',
        'image':    '0823182de4653fbdbcce27b83eadb6d9424b59af8129e96937af62500bc7a8b6',
        'ip':        '10.0.225.10',
        'port':    '',
        'volume':    '',
        'cmd':    '/usr/sbin/sshd -D',
        'cpu':    '10',
        'mem':    '1g',
        'swap':    '1g',
        'disk':    '40Gi',
    }
    params = urllib.urlencode(data)
    print params
    url = 'http://' + request.META['HTTP_HOST'] + "/api/create_container"
    print url
    req = urllib2.Request(url)
    response = urllib2.urlopen(req)
    res = response.read()
    print res
    return HttpResponse(res)


def create_container_test(request, *args, **kwargs):
    if request.method == 'GET':
        return render_to_response(request, 'create_container_test.html', {})
    data = {
    'hostname': 'docker23',
    'image':    '0823182de4653fbdbcce27b83eadb6d9424b59af8129e96937af62500bc7a8b6',
    'ip':        '10.0.225.10',
    'port':    '',
    'volume':    '',
    'cmd':    '/usr/sbin/sshd -D',
    'cpu':    '10',
    'mem':    '1g',
    'swap':    '1g',
    'disk':    '40Gi',
    }
    params = urllib.urlencode(data)
    print params
    url = 'http://' + request.META['HTTP_HOST'] + "/api/create_container"
    print url
    req = urllib2.Request(url)
    response = urllib2.urlopen(req)
    res = response.read()
    print res
    return HttpResponse(res)

