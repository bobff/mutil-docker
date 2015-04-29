#coding=utf-8
import simplejson
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods
import hashlib
from django.conf import settings
import random
from ..models import User
import datetime
from django.core.cache import cache

def set_token_cache(token, user):
    # request.session[validate_code] = user
    # request.session.set_expiry(settings.API_TIME_OUT)
    print 'set_token', token, user
    return cache.set(token, user, 9999)

def get_token_cache(token):
    print 'get_token', token, cache.get(token)
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

