from django.contrib import admin
from dockers.models import *

class HostAdmin(admin.ModelAdmin):
    list_display_links = ('name','ipv4','status')
    list_display = ('name','ipv4','status')
    list_filter = ['name','ipv4','status']
    search_fields = ['name','ipv4','status']
    ordering = ('name',)
admin.site.register(Host,HostAdmin)

# class HubAdmin(admin.ModelAdmin):
#     list_display_links = ('name',)
#     list_display = ('name','ipv4','port','remark')
#     list_filter = ['name','ipv4','port']
#     search_fields = ['name','ipv4','port','remark']
#     ordering = ('ipv4',)
# admin.site.register(Hub,HubAdmin)

class ContainerAdmin(admin.ModelAdmin):
    list_display_links = ('network_ipv4',)
    list_display = ('name','network_ipv4', 'host', 'cpu_share', 'mem_limit', 'swap_limit', 'disk_limit','end_date')
    list_filter = ['network_ipv4', 'host', 'cpu_share', 'mem_limit', 'swap_limit', 'disk_limit']
    search_fields = ['network_ipv4', 'host', 'cpu_share', 'mem_limit', 'swap_limit', 'disk_limit']
    ordering = ('network_ipv4',)
admin.site.register(Container, ContainerAdmin)