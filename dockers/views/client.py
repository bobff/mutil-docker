#coding=utf-8
import docker, uuid, os, simplejson, logging
from django.conf import settings
from functools import wraps
from multiprocessing import Process 
import subprocess
from ..models import Host, Container#, Image
from network.models import IPv4Pool
import paramiko
from random import choice
import string
import datetime
import time

log = logging.getLogger('mutil_docker')

def get_client(hostname):
    '''
        根据hostname 获取client对象
        settings文件里必须设置好CERTIFICATE_PATH 相应的目录下必须有ssl证书文件
    '''
    tls_config = docker.tls.TLSConfig(
        client_cert=(settings.CERTIFICATE_PATH + '/cert.pem',settings.CERTIFICATE_PATH + '/key.pem'),
        ca_cert=settings.CERTIFICATE_PATH + '/ca.pem',
        verify=True)
    
    try:
        client = docker.Client(base_url='https://'+hostname+':2376', tls=tls_config)
        res = client.ping()
    except:
        res = False

    # update database
    host = Host.objects.filter(name = hostname)
    if host:
        if res == 'OK':
            status = '01'
        else:
            status = '10'
        for h in host:
            h.status = status
            h.save()
    
    if res == 'OK':
        return client
    return False


class Client(object):
    """docstring for Client"""
    def __init__(self, host=None):
        self._host = host
        self._client = get_client(host)

    def _client_required(func):
        '''装饰器 确保client存在'''
        def handle_args(*args, **kwargs): #处理传入函数的参数
            if type(args[0]._client) == docker.Client:
                return func(*args, **kwargs)   #函数调用
            else:
                raise Exception, 'client error'
        return handle_args

    def _muti_process(func):
        '''装饰器 新进程中处理，防止请求超时'''
        def handle_args(*args, **kwargs): #处理传入函数的参数
            child_proc = Process(target=func, args=args)  
            child_proc.start() 
            return True
            
        return handle_args

    def get_client(self):
        return self._client

    @_client_required     
    def attach(self, container, stdout=True, stderr=True, stream=True, logs=True):
        return self._client.attach(container, stdout, stderr, stream, logs)

    def get_containers(self, all=False):
        '''从各个host获取containers'''

        hosts = Host.objects.filter(status='01')
        
        obj_list = []
        for h in hosts:
            try:
                client = get_client(h.name)
                containers = client.containers(all=all)
            except:
                containers = []
            for o in containers:
                o['hostname'] = h.name
                info = Container.objects.filter(id=o['Id']).order_by('network_ipv4')
                if not info:
                    info = Container(id=o['Id'], host=h)
                    info.save()
                else:
                    info = info[0]
                
                o['info'] = info
                
                tmp = o['Image'].split(str('%s:%s/')%(settings.DOCKER_HUB_HOST, settings.DOCKER_HUB_PORT))
                o['repotag'] = tmp[-1]
                obj_list.append(o)

        return obj_list

    def get_container_by_id(self, id):
        hosts = Host.objects.filter(status='01')
        for h in hosts:
            try:
                client = get_client(h.name)
                containers = client.containers(all=True)
            except:
                containers = []
            for o in containers:
                if o['Id'] == id:
                    o['hostname'] = h.name
                    info = Container.objects.filter(id=o['Id'])
                    if not info:
                        info = Container(id=o['Id'], host=h)
                        info.save()
                    else:
                        info = info[0]
                    
                    o['info'] = info
                
                    tmp = o['Image'].split(str('%s:%s/')%(settings.DOCKER_HUB_HOST, settings.DOCKER_HUB_PORT))
                    o['repotag'] = tmp[-1]

                    return o
        return None

    @_client_required
    def inspect_container(self, id):
        '''container详细信息'''
        if not id:
            return False
        obj = self._client.inspect_container(id)
        return obj

    def _create_hwaddr(self, ip):
        ip = ip.split('.')
        mac = '00:00'
        map10to16 = {}
        for i in range(10):
            map10to16[i] = str(i)
        map10to16[10] = 'A'
        map10to16[11] = 'B'
        map10to16[12] = 'C'
        map10to16[13] = 'D'
        map10to16[14] = 'E'
        map10to16[15] = 'F'
        for i in ip:
            i = int(i)
            mac += ':' + map10to16[i/16] + map10to16[i%16]
        return mac

    @_client_required
    def create_container(self, data):
        keys = {
            'ip'        : {'required':True}, 
            'ip_size'   : {'required':False, 'default':24}, 
            'port'      : {'required':False, 'default':''}, 
            'image'     : {'required':True},
            'hostname'  : {'required':True},
            'cmd'       : {'required':False, 'default':''},
            'cpu'       : {'required':False, 'default':0},
            'mem'       : {'required':False, 'default':''},
            'swap'      : {'required':False, 'default':''},
            'disk'      : {'required':False, 'default':''},
            'volume'    : {'required':False, 'default':''},
            'ipv4pool'  : {'required':False, 'default':''},
            'name'      : {'required':True},
            'prename'   : {'required':False, 'default':False},
            'passwd'    : {'required':False, 'default':''},
            'end_date'  : {'required':False, 'default': None},
            }

        for key in keys.keys():
            if keys[key]['required'] and not data.has_key(key):
                return False, '000, 参数有误， ' + key + ' is required.'
            elif not keys[key]['required'] and not data.has_key(key):
                data[key] = keys[key]['default']

        if type(data['ip_size']) != int:
            try:
                data['ip_size'] = int(data['ip_size'])
            except:
                data['ip_size'] = 24
        if type(data['cpu']) != int:
            try:
                data['cpu'] = int(data['cpu'])
            except:
                data['cpu'] = None
        if data['passwd'] == '' or data['passwd'] == None:
            data['passwd'] = ''.join([choice(string.ascii_letters+string.digits) for i in range(6)])
            
        start_date = datetime.date.today()
        data['start_date'] = start_date
        if data['end_date']:
            try:
                tmp = data['end_date'].split('-')
                datetime.date(int(tmp[0]), int(tmp[1]), int(tmp[2]))
            except:
                return False, '001, end_date 日期格式错误, 正确格式： xxxx-xx-xx'
        print data['start_date'], data['end_date']
        port    = get_port_bind_dict(data['port'])
        volume  = get_volume_bind_dict(data['volume'])
        host    = Host.objects.get(name=data['hostname'])
        pool    = IPv4Pool.objects.get(pk = data['ipv4pool'])
        if not pool.validate_ip(data['ip'], data['ip_size']):
            return False, '002, ip 地址有误'

        if data['prename'] == False:
            exist = Container.objects.filter(name=data['name']).exists()
            if exist:
                return False, '003, 容器名冲突'
        else:
            trylimit = 100
            for trycount in xrange(trylimit):
                append_name = '_' + ''.join([choice(string.digits) for i in range(6)])
                exist = Container.objects.filter(name=data['name'] + append_name).exists()
                if not exist:
                    data['name'] += append_name
                    break
            else:
                return False, '004, 容器太多，容器名后缀不够用啦'
            print 'rand a name',  data['name']
        print data
        c = self._client.create_container(data['image'],
            command         = data['cmd'],
            network_disabled= False, 
            detach          = True, 
            stdin_open      = True,
            tty             = True,
            cpu_shares      = data['cpu'], 
            mem_limit       = data['mem'], 
            memswap_limit   = data['swap'],
            ports           = tuple(port.keys()), 
            volumes         = [v['bind'] for v in volume.values()],
            name            = data['name']
            )
        
        print 'craete res', c
        container = Container(id=c['Id'], host_id=data['hostname'])
        container.net                   = pool 
        container.network_type          = "veth"
        container.network_ipv4          = data['ip']
        container.network_ipv4_size     = data['ip_size']
        container.network_ipv4_gateway  = pool.gateway
        container.network_link          = host.bridge
        container.network_name          = "eth0"
        container.network_hwaddr        = self._create_hwaddr(data['ip'])
        container.cpu_share             = data['cpu']
        container.mem_limit             = data['mem']
        container.swap_limit            = data['swap']
        container.login_name            = settings.DOCKER_DEFAULT_USER    #目前只能使用cnic    在不同系统中 创建自定义的用户名可能会出现问题 ，所以在image中创建好固定的
        container.login_pwd             = data['passwd']
        container.port_bind             = data['port']
        container.volume_bind           = data['volume']
        container.disk_limit            = data['disk']
        container.name                  = data['name']
        container.start_date            = data['start_date']
        container.end_date              = data['end_date']
        pool.register_ip(data['ip'])
        container.save()

        if not self.start_container(c['Id']):
            if self.remove_container(c['Id']):
                return False, '005, 容器启动失败'
            else:
                return False, '006, 容器启动失败。容器记录未清除。'
        
        
        # res = self.set_passwd(c['Id'], data['passwd'])
        # if not res:
        #     if self.remove_container(c['Id']):
        #         return False, '容器创建失败'
        #     else:
        #         return False, '容器创建失败。容器记录未清除。'
        return True, container

    @_client_required
    def start_container(self, id):
        if not id:
            return False
        # if True:
        try:
            container = Container.objects.get(id=id)
            lxc_conf = [
                {'Key':"lxc.network.type",          'Value':container.network_type},
                {'Key':"lxc.network.ipv4",          'Value': container.network_ipv4 + '/' + str(container.network_ipv4_size)},
                {'Key':"lxc.network.ipv4.gateway",  'Value':container.network_ipv4_gateway},
                {'Key':"lxc.network.flags",         'Value':"up"},
                {'Key':"lxc.network.link",          'Value':container.network_link},
                {'Key':"lxc.network.name",          'Value':container.network_name},
                {'Key':"lxc.network.hwaddr",        'Value':container.network_hwaddr},
            ]

            port    = get_port_bind_dict(container.port_bind)
            volume  = get_volume_bind_dict(container.volume_bind)
            self._client.start(id, 
                dns             = '8.8.8.8',  
                lxc_conf        = lxc_conf, 
                network_mode    = "none", 
                port_bindings   = port,
                binds           = volume,
                )
            print 'auto ssh'

            trylimit = 5
            for trycount in range(trylimit):
                # auto run and set passwd 
                ssh = paramiko.SSHClient()  
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())  
                print container.network_ipv4, settings.DOCKER_IMAGE_ROOT_PWD
                try:
                    ssh.connect(container.network_ipv4,22, 'root' , settings.DOCKER_IMAGE_ROOT_PWD) 
                    cmd1 = 'echo %s > /passwd.txt'%(container.login_pwd,)
                    print cmd1
                    stdin,stdout,stderr=ssh.exec_command(cmd1)  
                    # print stderr.read()    
                    cmd2 = 'sh /auto_run.sh' 
                    print cmd2
                    stdin,stdout,stderr=ssh.exec_command(cmd2)
                    # print stderr.read() 
                    cmd3 = 'echo %s:%s | chpasswd' % (container.login_name, container.login_pwd)
                    print cmd3
                    stdin,stdout,stderr=ssh.exec_command(cmd3)
                    # print stderr.read() 
                    ssh.close() 
                    break
                except Exception, e:
                    print 'connect try',trylimit, e
                    time.sleep(2)
                 
        except Exception, e:
            print e
            return False
        # return False
        # #获取aufs路径
        # obj = self.inspect_container(id)
        # path_cut = obj['HostsPath'].split('/')
        # path = '/'.join(path_cut[:-3]) + '/aufs/diff/' + id
        
        # #设置磁盘限额
        # if container.disk_limit:
        #     result = os.system('sudo mfssetquota -L ' + container.disk_limit + ' ' + path)
        # else:
        #     result = os.system('sudo mfsdelquota -L ' + path)
        return True

    # def set_passwd(self, id, pwd=None):
    #     try:
    #         container = Container.objects.get(id=id)
    #         ssh = paramiko.SSHClient()  
    #         ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())  
            
    #         ssh.connect(container.network_ipv4,22, 'root' , settings.DOCKER_IMAGE_ROOT_PWD)  
           
            
    #         if pwd == None:
    #             pwd = ''.join([choice(string.ascii_letters+string.digits) for i in range(6)])
            
    #         container.login_pwd = pwd
            
    #         # cmd = 'passwd'
    #         # print cmd
    #         # stdin, stdout, stderr = ssh.exec_command(cmd)  

    #         # # print 'out ', stdout.read()
    #         # # print 'err ', stderr.read()
    #         # stdin.write(container.login_pwd)
    #         # # print stdout.read()
    #         # # print 'err ', stderr.read()
    #         # stdin.write(pwd)   #简单交互，输入 ‘Y’ 
    #         # # print stdout.read()
    #         # # print 'err ', stderr.read()
    #         # stdin.write(pwd)  
    #         # # print stdout.read()
    #         # # print 'err ', stderr.read()

    #         cmd2 = 'echo %s:%s | chpasswd' % (container.login_name, container.login_pwd)
           
    #         stdin,stdout,stderr=ssh.exec_command(cmd2)
    #         stdin,stdout,stderr=ssh.exec_command('echo %s > /passwd.txt')
             
           
    #         container.save()
            

            
    #         ssh.close()  
    #     except:
    #         return False
    #     return True
            
    @_client_required
    def remove_container(self, id):
        if not id:
            return False

        try:
            obj = Container.objects.get(id=id)
            if obj.protected:
                print 'deleted'
                return False
            obj.net.release_ip(obj.network_ipv4)
            obj.delete()
            self._client.stop(id)
            self._client.remove_container(id)
            print 'remove container'
        except:
            return False
        return True

    @_client_required
    def stop_container(self, id):
        if not id:
            return False
        try:
            self._client.stop(id)
        except:
            return False
        return True

    @_client_required
    def  pause_container(self, id):
        if not id:
            return False
        try:
            self._client.stop(id)
        except:
            return False
        return True

    @_client_required
    def logs(self, id):
        if not id:
            return False

        return self._client.logs(id)
       
    @_client_required
    def commit(self, id, repository=None, tag=None, author=None, message=None):
        return self._do_commit(id,repository, tag, author, message)
        
    @_client_required
    @_muti_process
    def _do_commit(self, id, repository, tag, author, message):
        print 'start commit'
        return self._client.commit(id, repository=repository, tag=tag, message=message, author=author)

    @_client_required
    def version(self):
        return self._client.version()   
    
    @_client_required
    def info(self):
        return self._client.info()

    @_client_required
    def ping(self):
        return self._client.ping()

    def get_all_images(self):
        '''从各个host获取images'''
        hosts = Host.objects.filter(status='01')
        obj_list = []
        for h in hosts:
            obj_list += self.get_images(h.name)
        return obj_list

    def get_images(self, host=None):
        if host:
            client = get_client(host)
        else:
            client = self._client
            host   = self._host
        obj_list = []
        try:
            images = client.images()
        except:
            images = []
        for o in images:
            o['hostname'] = host
            for repotag in o['RepoTags']:
                o['regrepotag'] = repotag
                tmp = repotag.split(settings.DOCKER_HUB_HOST + ':' + str(settings.DOCKER_HUB_PORT) + '/',1)
                repotag = tmp[-1]
                o['repotag'] = repotag
                o['reg'] = settings.DOCKER_HUB_HOST + ':' + str(settings.DOCKER_HUB_PORT)
                repotag = repotag.split(':')
                o['repo'] = repotag[0]
                o['tag'] = repotag[1]
                obj_list.append(o)
        return obj_list

    @_client_required
    def inspect_image(self, id):
        obj = self._client.inspect_image(id)
        images = self.get_images()
        for image in images:
            if str(image['Id']).startswith(id):
                for item in image.items():
                    obj[item[0]] = item[1]
                break
            
        return obj

    def get_file_path(self, fdir, uid):
        path_split = ['mutil_docker_data', str(fdir), str(uid)]
        path = os.getcwd()
        for p in path_split:
            path += '/' + p
            if not os.path.exists(path):
                os.mkdir(path)
        return path

    def build(self, dockerfile, tag, supervisord=None, uid=None, login_name=None, login_pwd=None):
        if not dockerfile or not tag:
            return False
        self._do_build(dockerfile, tag, supervisord, uid, login_name, login_pwd)
        return True

    @_muti_process
    def _do_build(self, dockerfile, tag, supervisord, uid, login_name, login_pwd):
        if uid == None:
            uid = uuid.uuid4()
        uid = str(uid)
        path = self.get_file_path('dockerfile', uid)
        f = open(path+'/Dockerfile', 'w+')
        f.write(dockerfile)
        f.close()

        if supervisord:
            sf = open(path+'/supervisord.conf', 'w+')
            sf.write(supervisord)
            sf.close()
            f = open(path+'/Dockerfile', 'a')
            f.write('\nADD supervisord.conf /etc/supervisord.conf')
            f.close()

        popen = subprocess.Popen(['sudo', 'docker', 'build', '-t', tag, path], stdout = subprocess.PIPE)
        logf = open(path + '/build.log', 'a')
        logf.write('start build image\n')
        logf.flush()
        while True:
            next_line = popen.stdout.readline()
            print '[CMD] ', next_line
            if next_line == '' and popen.poll() != None:
                break
            logf.write(next_line)
            logf.flush()

        if popen.poll() == 0:
            new_tag = settings.DOCKER_HUB_HOST + ':' + str(settings.DOCKER_HUB_PORT) + '/' + tag
            popen = subprocess.Popen(['sudo', 'docker', 'tag', tag, new_tag], stdout = subprocess.PIPE)
            logf.write('\nstart tag image\n')
            logf.flush()
            while True:
                next_line = popen.stdout.readline()
                print '[CMD] ', next_line
                if next_line == '' and popen.poll() != None:
                    break
                logf.write(next_line)
                logf.flush()

            popen = subprocess.Popen(['sudo', 'docker', 'push', new_tag], stdout = subprocess.PIPE)
            logf.write('\nstart push image\n')
            logf.flush()
            while True:
                next_line = popen.stdout.readline()
                print '[CMD] ', next_line
                if next_line == '' and popen.poll() != None:
                    break
                logf.write(next_line)
                logf.flush()
            

        tmp = tag.strip().strip(':').split(':')
        if len(tmp) == 1:
            tmp.append('latest') 

        image_id = None
        popen = subprocess.Popen(['sudo', 'docker', 'images'], stdout = subprocess.PIPE)
        while True:
            next_line = popen.stdout.readline()
            if next_line == '' and popen.poll() != None:
                break
            line = next_line.split()
            if line[0] == tmp[0] and line[1] == tmp[1]:
                image_id = line[2]
                break

        # import MySQLdb   
        # try:
        #     db_info = settings.DATABASES['default']
        #     conn = MySQLdb.connect(host=db_info['HOST'],user=db_info['USER'],passwd=db_info['PASSWORD'],db=db_info['NAME'],port=int(db_info['PORT']))
        #     cur = conn.cursor()
        #     if login_name == None:
        #         login_name = ''
        #     if login_pwd == None:
        #         login_pwd = ''
        #     if dockerfile == None:
        #         dockerfile = ''
        #     if supervisord == None:
        #         supervisord = ''
        #     sql = "insert into dockers_image (build_id, code, name, tag, login_name, login_pwd, dockerfile, supervisord) "
        #     sql +=" values ('"+uid+"', '"+image_id+"', '"+tmp[0]+"', '"+tmp[1]+"', '"+login_name+"', '"+login_pwd+"', '"+dockerfile+"', '"+supervisord+"')";
        #     count = cur.execute(sql)
        #     conn.commit()
        #     cur.close()
        #     conn.close()
        #     logf.write('\ninsert into db\n')
        #     logf.write(sql + '\n')
        #     logf.flush()
        # except MySQLdb.Error,e:
        #      print "Mysql Error %d: %s" % (e.args[0], e.args[1])

        logf.close()

    @_client_required
    def remove_image(self, id):
        if not id:
            return False
        return self._client.remove_image(id)

    @_client_required
    def pull(self, repository, tag=None, uid=None):
        if not repository:
            return False
        if uid == None:
            self._client.pull(repository, tag=tag)
        else:
            name = repository
            if tag != None and tag != '':
                name = name + ':' + tag
            try:
                self._do_pull(settings.DOCKER_HUB_HOST + ':' + str(settings.DOCKER_HUB_PORT) + '/' + name, uid)
            except:
                print 1111111111111111111111        
        return True

    @_client_required
    @_muti_process
    def _do_pull(self, name, uid):

        popen = subprocess.Popen(['sudo', 'docker', '--tls', '-H=' + self._host + ':2376', 'pull', name], stdout = subprocess.PIPE, stderr = subprocess.PIPE)
        path = self.get_file_path('images_' + self._host, uid)
        logf = open(path + '/pull.log', 'a')
        logf.write('Start pull image   ' + name + '\n')
        logf.flush()
        while True:
            next_line = popen.stdout.readline()
            print '[CMD] ', next_line
            err_line = popen.stderr.readline()
            if err_line != '':
                logf.write(err_line)
                print '[ERR] ', err_line
            if next_line == '' and popen.poll() != None:
                break
            logf.write(next_line)
            logf.flush()
        logf.write('Finished pull ')
        logf.close()

    @_client_required
    @_muti_process
    def push(self, id):
        obj = self.inspect_image(id)
        path = self.get_file_path('images_' + self._host, id)
        logf = open(path + '/push.log', 'a')
        logf.write('Start push image   ' + obj['regrepotag'] + '\n')
        logf.flush()
        for line in self._client.push(obj['reg']+'/'+obj['repo'], tag=obj['tag'], stream=True):
            logf.write(line)
            logf.flush()
        logf.write('Finished push ')
        logf.close()
    

def get_port_bind_dict(port):
    port_bind = {}
    if not port:
        return port_bind
    port = port.split(';')
    for p in port:
        p = p.split(':')
        if len(p) == 1:
            port_bind[p[0]] = None
        if len(p) == 2:
            port_bind[p[1]] = p[0]
        if len(p) == 3:
            port_bind[p[2]] = p[0] + ':' + p[1] 
    return port_bind
def get_volume_bind_dict(volume):
    volume_bind = {}
    if not volume:
        return volume_bind

    volume = volume.split(';')
    for v in volume:
        v = v.split(':')
        if len(v) == 2:
            volume_bind[v[0]] = {
                'bind': v[1],
                'ro': False
            }
        if len(v) == 3:
            if v[2] == 'ro' or v[2] == 'RO':
                v[2] = True
            else:
                v[2] = False
            volume_bind[v[0]] = {
                'bind': v[1],
                'ro': v[2]
            }
    return volume_bind