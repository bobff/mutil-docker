#coding=utf-8
from django.db import models
from network.models import IPv4Pool
from dockers.models import Host

class User(models.Model):
    name        = models.CharField('用户名', max_length=128, primary_key = True)
    ipv4        = models.IPAddressField('绑定IP地址', null=True, blank=True)
    password    = models.CharField('密码', max_length=128)
    active      = models.BooleanField('激活', default=True)

    class Meta:
        verbose_name = 'API用户'
        verbose_name_plural = verbose_name

    def __unicode__(self):
        return self.name

class Log(models.Model):
    name        = models.CharField('用户', max_length=128)
    ipv4        = models.IPAddressField('IP地址')
    uri         = models.TextField('请求接口')
    get_args    = models.TextField('GET参数', blank=True)
    post_args   = models.TextField('POST参数', blank=True)
    res         = models.CharField('结果', max_length=20, blank=True)
    error       = models.TextField('错误', null=True, blank=True)
    data_len    = models.IntegerField('数据长度', null=True, blank=True)

# class IPProperty(models.Model):
#     user = models.ForeignKey(User, verbose_name='用户')
#     pool = models.ForeignKey(IPv4Pool, verbose_name='IP地址池')

#     class Meta:
#         verbose_name = 'IP资源'
#         verbose_name_plural = verbose_name

# class HostProperty(models.Model):
#     user = models.ForeignKey(User, verbose_name="用户")
#     host = models.ForeignKey(Host, verbose_name="宿主机")

#     class Meta:
#         verbose_name = '主机资源'
#         verbose_name_plural = verbose_name

class CreatePermission(models.Model):
    user = models.ForeignKey(User, verbose_name="用户")
    host = models.ForeignKey(Host, verbose_name="宿主机")
    pool = models.ForeignKey(IPv4Pool, verbose_name="IP资源")
    image = models.CharField("默认镜像", max_length=200)
    cpu  = models.IntegerField('cpu', null=True, blank=True)
    mem = models.CharField('mem', max_length=100, null=True, blank=True)
    disk = models.CharField('disk', max_length=100, null=True, blank=True)
    port_bind = models.CharField('port_bind', max_length=200, null=True, blank=True)
    volume_bind = models.CharField('volume_bind', max_length=200, null=True, blank=True)
    num  = models.IntegerField('创建数量限制')

    class Meta:
        verbose_name = 'API用户创建容器权限'
        verbose_name_plural = verbose_name