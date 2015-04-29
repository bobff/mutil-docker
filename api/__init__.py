# #coding=utf-8
# from functools import wraps
# from django.utils.decorators import available_attrs

# def protected_resource():
#     def decorator(view_func):
#         @wraps(view_func, assigned=available_attrs(view_func))
#         def _wrapped_view(request, *args, **kwargs):
#             token = request.GET.get('token', None)
            
#             r = HelpDeskUser.objects.filter(user = request.user, role='1')
#             if r.exists():
#                 return view_func(request, *args, **kwargs)
#             return HttpResponse('权限不足！')
#         return _wrapped_view
#     return decorator