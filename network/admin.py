from django.contrib import admin
from .models import *

class IPv4PoolAdmin(admin.ModelAdmin):
    list_display_links = ('net',)
    list_display =  ('net','start_ip','end_ip', 'ip_count', 'ip_used_count', 'remarks')
    list_filter = ['net']
    search_fields = ['net','start_ip','end_ip']
    ordering = ('net',)
admin.site.register(IPv4Pool,IPv4PoolAdmin)

class IPv4UsageAdmin(admin.ModelAdmin):
    list_display_links = ('ip',)
    list_display =  ('ip','pool', 'host', 'remarks',)
    list_filter = ['pool']
    search_fields = ['ip','pool', 'host', 'remarks']
    ordering = ('ip',)
admin.site.register(IPv4Usage,IPv4UsageAdmin)
