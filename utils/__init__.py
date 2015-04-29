#coding=utf-8

"""
该模块包含系统开发、运行的底层工具

@version: $Id$
@author: U{gaobo<mailto:gaobo@bjtu.edu.cn>}
@contact: gaobo@bjtu.edu.cn
@see: 参考资料链接等等
@license: GPL
@todo:
@bug:

"""

import re
import random
  
from django.core.paginator import Paginator
from django.http import HttpResponse, Http404
from django.conf import settings
from django.shortcuts import render_to_response as dj_render_to_response
from django.template import RequestContext
from django.utils import simplejson

class Page:
    '''
      分页显示工具，
      该工具封装了django的Paginator。
    '''
    def __init__(self, objs, c, p):
        '''
        @type objs: list
        @param objs: 需要分页显示的对象列表。
        @type c: number
        @param c: 每页的对象数量
        @type p: number
        @param p: 要显示第几页

        @rtype: Page
        @return: 返回Page对象

        '''
        self._pageor = Paginator(objs, c)
        if p > self._pageor.num_pages:
            p = self._pageor.num_pages
        elif p < 1:
            p = 1
        
        self._page = self._pageor.page(p)


        self.count = self._pageor.count
        self.num_pages = self._pageor.num_pages
        self.per_page = c
        self.start_page = 1
        self.end_page = self.num_pages

        self.object_list = self._page.object_list
        self.num_cur_page = self._page.number
        self.start_index = self._page.start_index()
        self.end_index = self._page.end_index()


        _t = [self.num_cur_page]
        while len(_t) < 5 and (_t[len(_t)-1] < self.num_pages or _t[0] > 1):
            if _t[0] > 1:
                _t = [_t[0] -1] + _t
            if _t[len(_t)-1] < self.num_pages:
                _t = _t + [_t[len(_t)-1] + 1]
        if len(_t) == 1:
            _t = []  
        self.page_range = _t

    def has_next(self):
        '''
           判断是否有后一页
        @rtype: boolean
        '''
        return self._page.has_next()

    def has_previous(self):
        '''
           判断是否有前一页
        @rtype: boolean
        '''
        return self._page.has_previous()

    def next_page_number(self):
        '''
           返回后一页的页号
        @rtype: number
        '''
        return self._page.next_page_number()

    def previous_page_number(self):
        '''
           返回前一页的页号
        @rtype: number
        '''

        return self._page.previous_page_number()

def get_page(objs, request, perpage=0):
    '''
      方便程序调用，返回Page对象

    @type objs: list
    @param objs: 需要分页显示的对象列表。
    @type request: django httprequest
    @param request: request中包含page变量，默认是首页
    @type perpage: number
    @param perpage: 每页的对象数量，默认数值是20

    @rtype: Page
    @return: 返回Page对象
    '''
    try:
        page_num = int(request.GET.get('page', 1))
    except ValueError:
        page_num = 1    

    if perpage == 0:
        try:
            perpage = int(request.GET.get('perpage', 15))
        except ValueError:
            perpage = 15

    return Page(objs, perpage, page_num)

def render_to_response(request, template, dic={}):
    '''
      封装了django的render_to_response方法，目的是将request传入context_instance中，
      在模板中可以使用user等变量， template, dic 类似 django 中render_to_response的使用
    '''
    return dj_render_to_response(template, dic, 
                 context_instance=RequestContext(request))

def render_to_response_json(dict):
    '''
      封装了django的render_to_response_json方法，返回json数据

    @type dict: dict
    @param dict: 传入字典数据

    @rtype: HttpResponse
    @return: 返回json数据
    '''
    return HttpResponse(simplejson.dumps(dict), mimetype = 'application/json')

def dispatch_url(urlmap, url, request):
    '''
      转发 url地址，若没有对应的地址配置，生成Http 404错误
    '''
    for p in urlmap.keys():
        foo_url = re.sub(p, "", url)
        if url != foo_url:
            obj = urlmap[p]
            url = foo_url
            return obj().root(request, url)
    raise Http404

def get_rand_str(n):
    '''
     生成长度为n的随机字符串
    ''' 
    str = '' 
    while len(str) < n: 
      temp = chr(97+random.randint(0,25))
      if str.find(temp) == -1 :
        str = str.join(['',temp])
    return str

def get_abs_attach_fname(str):
    '''
      返回附件文件在服务器上的绝对目录
    ''' 
    return settings.MEDIA_ROOT + str
