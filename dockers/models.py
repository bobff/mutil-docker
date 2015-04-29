#coding=utf-8
from django.db import models
from network.models import IPv4Pool

class Host(models.Model):
    STATUS_ON       = '01'
    STATUS_OFF      = '10'
    status_choices  = (
        (STATUS_ON,  '在线'),
        (STATUS_OFF, '离线'),
        )

    name        = models.CharField('主机名', max_length=100, primary_key = True)
    ipv4        = models.IPAddressField('IP地址')
    gateway     = models.IPAddressField('Gateway')
    bridge      = models.CharField('docker网桥', max_length=100)
    docker_v    = models.CharField('docker版本', max_length=100,null=True, blank=True)
    api_v       = models.CharField('docker remote api 版本', max_length=100,null=True, blank=True)
    kernel      = models.CharField('kernel', max_length=100, null=True, blank=True)
    info        = models.TextField('info',null=True, blank=True)
    status      = models.CharField('状态', max_length=2, choices=status_choices)

    def get_status(self):
        tmp = dict(self.status_choices)
        if tmp.has_key(self.status):
            return tmp[self.status]
        return None

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = '宿主机'
        verbose_name_plural = verbose_name


class Container(models.Model):
    id              = models.CharField('编号', max_length=200, primary_key=True)
    host            = models.ForeignKey(Host, verbose_name='宿主机')
    net             = models.ForeignKey(IPv4Pool, verbose_name="所属网段", null=True)
    network_type    = models.CharField('lxc.network.type', max_length=100)
    network_ipv4    = models.IPAddressField('lxc.network.ipv4', null=True, blank=True)
    network_ipv4_size    = models.IntegerField('子网大小', default=24, null=True, blank=True)
    network_ipv4_gateway = models.IPAddressField('lxc.network.ipv4.gateway', null=True, blank=True)
    network_link    = models.CharField('lxc.network.link', max_length=100, null=True, blank=True)
    network_name    = models.CharField('lxc.network.name', max_length=100, null=True, blank=True)
    network_hwaddr  = models.CharField('lxc.network.hwaddr', max_length=100, null=True, blank=True)
    submit_time     = models.DateTimeField('提交时间', auto_now_add=True)
    cpu_share       = models.IntegerField('CPU权重', null=True, blank=True)
    mem_limit       = models.CharField('内存限额', max_length=100, null=True, blank=True)
    swap_limit      = models.CharField('交换区限额', max_length=100, null=True, blank=True)
    disk_limit      = models.CharField('磁盘限额', max_length=100, null=True, blank=True)
    login_name      = models.CharField('登陆名', max_length=100, null=True, blank=True)
    login_pwd       = models.CharField('登陆密码', max_length=100, null=True, blank=True)
    port_bind       = models.CharField('端口绑定', max_length=100, null=True, blank=True)
    volume_bind     = models.CharField('磁盘挂载', max_length=100, null=True, blank=True)
    name            = models.CharField('名称', max_length=100, null=True, blank=True)
    start_date      = models.DateField('开始时间', null=True, blank=True)
    end_date        = models.DateField('到期时间', null=True, blank=True)
    protected       = models.BooleanField('受保护容器', default=False)

    class Meta:
        verbose_name = '容器'
        verbose_name_plural = verbose_name


# class Image(models.Model):
#     build_id    = models.CharField('创建ID', max_length=200, unique=True)
#     code        = models.CharField('编号', max_length=200, null=True, blank=True)
#     name        = models.CharField('名称', max_length=100)
#     tag         = models.CharField('标签', max_length=100, unique=True)
#     login_name  = models.CharField('登录账户', max_length=128, null=True, blank=True)
#     login_pwd   = models.CharField('登录密码', max_length=128, null=True, blank=True)
#     dockerfile  = models.TextField('dockerfile', null=True, blank=True)
#     supervisord = models.TextField('supervisord', null=True, blank=True)
#     remarks     = models.TextField('备注', null=True, blank=True)

#     hosts       = models.ManyToManyField(Host, verbose_name='宿主机')
#     inhub       = models.BooleanField('仓储')

#     class Meta:
#         verbose_name = '镜像'
#         verbose_name_plural = verbose_name
