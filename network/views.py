#coding=utf-8
import docker 
import simplejson

from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseNotFound

from .models import IPv4Pool, IPv4Usage

def index(request):
    return HttpResponseRedirect('/network')

def required_request_method(method):
    def handle_func(func):
        def handle_args(request, *args, **kwargs):
            if (type(method)  == list and request.method in method) or (type(method) == str and request.method == method):
                return func(request, *args, **kwargs)
            return HttpResponseNotFound()
        return handle_args
    return handle_func

# def required_request_method(method):
#     def decorator(view_func):
#         @wraps(view_func, assigned=available_attrs(view_func))
#         def _wrapped_view(request, *args, **kwargs):
#             r = HelpDeskUser.objects.filter(user = request.user, role='2')
#             if r.exists():
#                 return view_func(request, *args, **kwargs)
#             return HttpResponse('权限不足！')
#         return _wrapped_view
#     return decorator

@required_request_method('GET')
def ajax_get_free_ip_range(request):
    
    pool = request.GET.get('pool')
    if not pool:
        return HttpResponse(simplejson.dumps({'data':[]}), content_type = 'application/json')

    pobj = IPv4Pool.objects.get(pk=pool)
    return HttpResponse(simplejson.dumps({'data':pobj.get_free_ip_range()}), content_type = 'application/json')

@required_request_method('POST')
def ajax_register_ip(request):
    pool = request.POST.get('pool')
    ip = request.POST.get('ip')
    remarks = request.POST.get('remarks')

    if not pool or not ip:
        res = 0
    else:
        pobj = IPv4Pool()
        pobj.pool_id = pool
        pobj.ip = ip
        pobj.remarks = remarks
        try:
            pobj.save()
            res = 1
        except:
            res = 0

    return HttpResponse(simplejson.dumps({'res':res}), content_type = 'application/json')
