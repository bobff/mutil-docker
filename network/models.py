#coding=utf-8
from django.db import models
import struct,socket
from django.db.models import Min,Max,Sum 

class IPv4Pool(models.Model):
    net         = models.IPAddressField('网段') 
    size        = models.IntegerField('子网大小')
    start_ip    = models.IPAddressField('起始IP')
    end_ip      = models.IPAddressField('结束IP')
    gateway     = models.IPAddressField('gateway')
    remarks     = models.TextField('备注', null=True, blank=True)
    ip_count    = models.IntegerField('IP地址总数', null=True, blank=True)
    ip_used_count = models.IntegerField('已用IP地址数', null=True, blank=True)
    start_ip_int  = models.IntegerField('起始IP(int)', null=True, blank=True)
    end_ip_int    = models.IntegerField('结束IP(int)', null=True, blank=True)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        max_used_ip_int = self.ipv4usage_set.all().aggregate(Max('ip_int'))
        min_used_ip_int = self.ipv4usage_set.all().aggregate(Min('ip_int'))
        print max_used_ip_int, min_used_ip_int, min_used_ip_int < self.start_ip_int, max_used_ip_int > self.end_ip_int, self.end_ip_int
        if (type(min_used_ip_int) == int and min_used_ip_int < self.start_ip_int) or (type(max_used_ip_int) == int and max_used_ip_int > self.end_ip_int):
            raise Exception('IPv4Usage record out of range!')

        self.ip_count = int(self.end_ip.split('.')[3]) - int(self.start_ip.split('.')[3]) + 1
        self.ip_used_count = self.ipv4usage_set.all().count()
        self.start_ip_int = ipv4_from_string(self.start_ip)
        self.end_ip_int = ipv4_from_string(self.end_ip)
        return super(IPv4Pool,self).save(force_insert, force_update, using, update_fields)

    def get_free_ip_range(self, num = -1):
        print 'get %s free ips' % (num, )
        free_ip_list = []
        count = 0
        used_ip_list = [u.ip_int for u in self.ipv4usage_set.all().order_by('ip_int')]
        used_ip_list_len = len(used_ip_list)
        used_index = 0
        for i in xrange(self.start_ip_int, self.end_ip_int+1):
            if used_index < used_ip_list_len and i == used_ip_list[used_index]:
                used_index += 1
            else:
                if num >= 0 and count == num:
                    break
                count += 1
                free_ip_list.append(ipv4_to_string(i))
        print free_ip_list
        return free_ip_list

    def get_free_ip(self):
        res = self.get_free_ip_range(1)
        return len(res) > 0 and res[0] or None

    def register_ip(self, ip, host=None, remarks=None):
        if type(ip) == str or type(ip) == unicode:
            ip_int = ipv4_from_string(ip)
        elif type(ip) == int:
            ip_int = ip
        else:
            return False
        
        if ip_int >= self.start_ip_int and ip_int <= self.end_ip_int:
            obj = IPv4Usage.objects.get_or_create(pool=self, ip=ip)
            if not obj[1]:
                return False
            obj = obj[0]
            obj.host = host
            obj.remarks = remarks 
            try:
                obj.save()
                self.ip_used_count += 1
                super(IPv4Pool,self).save()
            except:
                return False
            return True
        return False

    def release_ip(self, ip):
        try:
            obj = self.ipv4usage_set.get(ip=ip)
            obj.delete()
        except:
            return False
        else:
            self.ip_used_count -= 1
            super(IPv4Pool,self).save()
        return True

    def validate_ip(self, ip, size=None):
        if size == None:
            ips = ip.split('/')
            if not len(ips) == 2:
                print 11111111111111
                return False
            ip = ips[0]
            size = ips[1]
        ip_int = ipv4_from_string(ip)
        if self.size != size or ip_int < self.start_ip_int or ip_int > self.end_ip_int:
            return False
        return True

    class Meta:
        verbose_name = 'IP地址池'
        verbose_name_plural = verbose_name

    def __unicode__(self):
        return self.net + '/' + str(self.size) + '(' + self.start_ip + '-' + self.end_ip + ')'

class IPv4Usage(models.Model):
    pool    = models.ForeignKey(IPv4Pool, verbose_name='网段')
    ip      = models.IPAddressField('IP地址', unique=True)
    ip_int  = models.IntegerField('IP', null=True, blank=True)
    host    = models.CharField('宿主机', max_length=100, null=True, blank=True)
    remarks = models.TextField('备注', null=True, blank=True)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.ip_int = ipv4_from_string(self.ip)
        return super(IPv4Usage,self).save(force_insert, force_update, using, update_fields)

    class Meta:
        verbose_name = 'IP地址使用记录'
        verbose_name_plural = verbose_name

# ipv4数字地址 
def ipv4_to_string(ipv4):
    ipv4_n = socket.htonl(ipv4)
    data = struct.pack('I', ipv4_n)
    ipv4_string = socket.inet_ntop(socket.AF_INET, data)
    return ipv4_string
def ipv4_from_string(ipv4_string):
    data = socket.inet_pton(socket.AF_INET, ipv4_string)
    ipv4_n = struct.unpack('I', data)
    ipv4 = socket.ntohl(ipv4_n[0])
    return ipv4