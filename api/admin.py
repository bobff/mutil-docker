from django.contrib import admin
from .models import *

class UserAdmin(admin.ModelAdmin):
    list_display_links = ('name',)
    list_display =  ('name','active')
    list_filter = ['active']
    search_fields = ['name']
    ordering = ('name',)
admin.site.register(User,UserAdmin)

# class IPPropertyAdmin(admin.ModelAdmin):
#     list_display_links = ('user',)
#     list_display =  ('user','pool')
#     # list_filter = ['active']
#     search_fields = ['user']
#     ordering = ('user',)
# admin.site.register(IPProperty,IPPropertyAdmin)

class CreatePermissionAdmin(admin.ModelAdmin):
    list_display_links = ('user',)
    list_display =  ('user','host','pool','image','num')
    search_fields = ['user']
    ordering = ('user',)
admin.site.register(CreatePermission,CreatePermissionAdmin)