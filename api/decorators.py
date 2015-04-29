#coding=utf-8
from functools import wraps
from django.utils.decorators import available_attrs
from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponseNotFound, HttpResponse
import hashlib
import simplejson
from .models import User, Log
from .views.token import get_token_cache

DEBUG = True

# def protected_resource(view_func):
#     def handle_args(*args, **kwargs): #处理传入函数的参数
#         @wraps(view_func, assigned=available_attrs(view_func))
#         def _wrapped_view(request, *args, **kwargs):
#             token = request.GET.get('token', None)
            
#             r = HelpDeskUser.objects.filter(user = request.user, role='1')
#             if r.exists():
#                 return view_func(request, *args, **kwargs)
#             return HttpResponse('权限不足！')
#         return _wrapped_view
#     return handle_args

def protected_resource():
    def decorator(view_func):
        @wraps(view_func, assigned=available_attrs(view_func))
        def _wrapped_view(request, *args, **kwargs):
            token = request.GET.get('token')
            valid = False
            try:
                if token:
                    user_cache = get_token_cache(token)
                    if user_cache != None:
                        user = User.objects.get(name = user_cache)
                        request.api_user = user
                        valid = True
            except:
                pass
            if valid:
                return view_func(request, *args, **kwargs)
            return HttpResponse( simplejson.dumps({'res':False, 'err':'validate failed'}), mimetype = 'application/json')
        return _wrapped_view
    return decorator


def add_log():
    def decorator(view_func):
        @wraps(view_func, assigned=available_attrs(view_func))
        def _wrapped_view(request, *args, **kwargs):
            res = view_func(request, *args, **kwargs)
            log = Log()
            log.name        = request.GET.get('user')
            log.ipv4        = request.META['REMOTE_ADDR']
            log.uri         = request.META['PATH_INFO']
            log.get_args    = request.GET
            log.post_args   = request.POST
            res._container = simplejson.loads(res._container)
            if res._container.has_key('res'):
                log.res = res._container['res']
            if res._container.has_key('error'):
                log.error = res._container['error']
            if res._container.has_key('data'):
                log.error = res._container['data']
            log.save()
            return res
        return _wrapped_view
    return decorator