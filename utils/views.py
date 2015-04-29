#coding=utf-8

"""
该模块包含系统开发Web视图开发框架

@version: $Id$
@author: U{gaobo<mailto:gaobo@bjtu.edu.cn>}, U{jesuit}
@contact: gaobo@bjtu.edu.cn
@see: 参考资料链接等等
@license: GPL
@todo:
@bug:

"""
import re
from datetime import datetime

#import ho.pisa as pisa
import cStringIO as StringIO
import cgi
import csv

from django.forms import ModelForm
from django.forms.models import model_to_dict
from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponse, Http404, HttpResponseBadRequest
from django.template.loader import get_template
from django.template import Context

from utils import get_page, render_to_response, get_rand_str, get_abs_attach_fname, render_to_response_json

class AbsView(object):
    """
    Web视图框架的抽象类，对于一般的对象操作包含基本操作CRUD，即所谓的新建、删除、修改、查询。该类
     基于此种思想，抽象出对于对象的的基本操作，置于视图之中，并加入url配置与转发。
    """
    
    DefaultModel = None
    """
    每个view会对应一个所操作的model。
    """    
    urlmap = {}
    """
    url配置
    """
    template_dir = ""
    """
    模板目录
    """
    csv_columns = None
    '''
    导出excel的表头文件
    '''
    
    def root(self, request, url):
        """
        解析、转发url到相应的函数中，若没有对应的配置，返回404错误。
        """
        for key in self.urlmap.keys():

            m = re.match(key, url)
            
            if m:
                mflag = True
                fun_name = self.urlmap[key][0]
                template = self.urlmap[key][1]
                
                if not template:
                    template = fun_name
                    
                template = "%s%s.html" %(self.template_dir, template)
                
                try:
                    func =  self.__getattribute__(fun_name)
                except:
                    func = None
                
                if func and callable(func):
                    return func(request, template, **(m.groupdict()))

        raise Http404

    def list(self, request, template):
        '''
           抽象方法，处理对象列表与对象搜索。
        '''
        raise NotImplementedError("abstract")
    
    def add(self, request, template):
        '''
           抽象方法，处理对象新建。
        '''
        raise NotImplementedError("abstract")
    
    def update(self, request, id, template):
        '''
           抽象方法，处理对象更新。
        '''
        raise NotImplementedError("abstract")
    
    def view(self, request, id, template):
        '''
           抽象方法，处理单一对象显示。
        '''
        raise NotImplementedError("abstract")
    
    def delete(self, request, id, template):
        '''
           抽象方法，处理单一对象删除。
        '''
        raise NotImplementedError("abstract")
    
    def query(self, request, template):
        '''
           抽象方法，显示查询页面。
        '''
        raise NotImplementedError("abstract")
    
    def csv_export(self, request, p_list, cols = None):
        '''
           处理对象列表时，做excel输出。
        '''
        
        def u2g(str):
            return str.decode('utf-8').encode('gb18030')
    
        def d2g(string):
            try:
                string.decode('utf-8').encode('gb18030')
            except:
                try:
                   string = string.encode('gb18030') 
                except:
                    pass
            return str(string)
        
        def get_csv_cell(p, k, index):
            if k == "forloop.count":
                return str(index+1)
            if type(k)==list:
                value = p
                for key in k:
                    if hasattr(value, key):
                        value = getattr(value,key)
                        if callable(value): value = value()
                    else:
                        value=""
                        break
                return  d2g(value)
            else:
                if hasattr(p, k):
                    value = getattr(p, k)
                    if callable(value): value = value()
                    return d2g(value)
                else:
                    return ""
                
        # Create the HttpResponse object with the appropriate CSV header.
        response = HttpResponse(mimetype='text/csv')
        response['Content-Disposition'] = 'attachment; filename=excel.csv'
        writer = csv.writer(response)
        
        if cols:
            csv_columns = []
            for i in self.csv_columns:
                if i[0].decode("utf-8") in cols:
                    csv_columns.append(i)
        else:
            csv_columns = self.csv_columns

        writer.writerow([u2g(i) for i, j in csv_columns])
        for index, p in enumerate(p_list):            
            re_list = [get_csv_cell(p, j, index) for i, j in csv_columns]
            writer.writerow(re_list)
               
        return response 
    
class AbsDefaultView(AbsView):
    '''
    该类实现抽象类AbsView中所定义的抽象方法，实现了CRUD的具体操作，一般方法均可从改类继承
    '''
    
    DefaultForm = None
    '''update,add时的表单Form'''

    UseDjangoForm = False
    '''是否使用Django原生的Form来生成表单'''

    list_args = {}
    ''' 
     列表时的filter参数， 类似：{'name':'name__contains', 'origin':'origin_pk'}
     取args['name__contains']= request.GET.get('name', None).
    filter(**args)
    '''
    
    def _get_list(self, request):
        """   
           该方法在子类中一般需要重写。对于对象列表的显示，有时候操作的基础并不是所有对象。
           比如由于某些权限限制，普通用户只能看到自己的相关项目，学院院长可以看到本学院的
           项目等等的需求，在list之前进行必要的操作。默认返回所有对象。
                   
        @type request: HttpRequest
        @param request: HttpRequest，从中取得user信息，做权限判断。
        """
        return self.DefaultModel.objects.all()

    def _get_add_dicts(self, request):
        '''
           该方法在子类中一般需要重写。除去对应的o以外，add与update 页面中需要显示的数据，
           比如：add，update中的下拉菜单对应的字典。
        '''
        dicts = {}
        return dicts
    
    def _get_update_dicts(self, request, o=None):
        '''
           该方法在子类中一般需要重写。除去对应的o以外，add与update 页面中需要显示的数据，
           比如：add，update中的下拉菜单对应的字典。
        '''
        dicts = {}
        return dicts
    
    def _get_view_dicts(self, request, o):
        '''
           该方法在子类中一般需要重写。除去对应的o以外，view 页面中需要显示的数据，
           比如：为了显示某些工作流的状态等。
        '''
        dicts = {}
        return dicts
    
    def _get_list_dicts(self, request):
        '''
           该方法在子类中一般需要重写。list 页面中需要显示的数据，
           比如：为了显示选择参数等。
        '''
        dicts = {}
        return dicts
    
    def _before_add(self, request):
        '''
           该方法在子类中一般需要重写。save方法中，执行o.save()之前所要执行的动作。
           比如：为了显示某些工作流的状态等。
        '''
        pass
    
    def _after_add(self, request, o):
        '''
           该方法在子类中一般需要重写。save方法中，执行o.save()之后所要执行的动作。
           比如：为了显示某些工作流的状态等。
        '''
        pass
        
    def _before_update(self):
        '''
           该方法在子类中一般需要重写。save方法中，执行o.save()之前所要执行的动作。
           比如：为了显示某些工作流的状态等。
        '''
        pass
    
    def _after_update(self, request, o):
        '''
           该方法在子类中一般需要重写。除去对应的o以外，view 页面中需要显示的数据，
           比如：为了显示某些工作流的状态等。
        '''
        pass
    
    def _view_argus(self, request, o):
        '''
           该方法在子类中一般需要重写。除去对应的o以外，view 页面中需要显示的数据，
           比如：为了显示某些工作流的状态等。
        '''
        return {}
    
    
    def list(self, request, template):
        """
        实现对象的列表与查询，该方法在子类中一般不需要重写
        """
        u = request.user
        ls = self._get_list(request)
        
        args = {}
        for ak in self.list_args.keys():
            if re.search('_doption$', ak):
                if request.GET.get(ak , None):
                    datestr = (request.GET.get(ak, None)).split('-')
                    args[str(self.list_args.get(ak))] = datetime.strptime((''.join((datestr[0],'-',datestr[1],'-01'))), '%Y-%m-%d')
            elif re.search('_option$', self.list_args.get(ak)):
                if request.GET.get(ak, None) and request.GET.get(ak + '_option', None):
                    args[str(ak+'__'+request.GET.get(ak + '_option', None))] = str(request.GET.get(ak, None))
            else:
                if request.GET.get(ak, None):
                    try:
                        args[str(self.list_args.get(ak))] = str(request.GET.get(ak, None))
                    except UnicodeEncodeError:
                        args[str(self.list_args.get(ak))] = request.GET.get(ak, None)
                     
        pri_contains = request.GET.get("pcontains", None)
        if pri_contains:
            ls = ls.model.objects_uc.filter_by_username_contains_pri(pri_contains, ls)
           
        pri = request.GET.get("p", None)
        if pri:    
            order = 0
            ls = ls.model.objects_uc.filter_by_jobnum_str(pri, ls, order)
            
        attstr = request.GET.get("a",None)
        if attstr: 
            order = 1           
            ls = ls.model.objects_uc.filter_by_jobnum_str(attstr, ls, order)
        print args        
        ls = ls.filter(**args)
                
        if(request.GET.get('excel')):
            if request.method == "POST":
                cols = request.POST.getlist("cols")
                return self.csv_export(request, ls, cols)

        p = get_page(ls, request)
        c_list = []
        if self.csv_columns:
            for c in self.csv_columns:
                c_list.append(c[0].decode("utf-8"));
        list_dicts = {'p':p, 'excel_cs':c_list}
        list_dicts.update(self._get_list_dicts(request))
        
        return render_to_response(request, template, list_dicts )   
    
    def query(self, request, template):
        """
        实现对象的查询页面显示，该方法在子类中一般不需要重写
        """
        if request.method == 'POST':
            """处理下url，免得字段太多，url太长，不美。Contract里面已经用起来了，其他模块可以用"""
            redirect_url = "../?"
            for p in request.POST:
                if request.POST[p]: redirect_url += "&" + p + "=" + request.POST[p]            
            return HttpResponseRedirect(redirect_url)
        return render_to_response(request, template, self._get_update_dicts(request) ) 
    
    def _get_view_object(self, request, id):
        return self.DefaultModel.objects.get(pk = id)

    def view(self, request, template, id):
        """
        实现单一对象的显示，该方法在子类中一般不需要重写
        """
        o = self._get_view_object(request, id)
        if o == None:
            return HttpResponseRedirect('/')
        
        if(request.GET.get('pdf')):
            return self.create_pdf(self.template_dir+'/pdf.html', o)

        dict = {'o':o, }
        dict.update(self._get_view_dicts(request, o))
        dict.update(self._view_argus(request, o))
        
        return render_to_response(request, template, dict, )    

    def delete(self, request,template, id):
        """
           实现单一对象的删除，该方法在子类中一般不需要重写
        """

        o = self.DefaultModel.objects.get(pk = id)
        o.delete()
        
        if request.GET.get('refer'):
            return request.GET.get('refer')
        else:
            return HttpResponseRedirect('../../')
    
    def add(self, request, template):
        """
           实现对象的新建，该方法在子类中一般不需要重写
        """ 
        o = self.DefaultModel()
        update_dicts = self._get_add_dicts(request)

        if request.method != 'POST':
            if self.UseDjangoForm:
                f = self.DefaultForm(o)
                update_dicts['form'] = str(f)
           
            return render_to_response(request, template, update_dicts, )
        
        if settings.DEBUG:
            print request.POST
            
        f = self.DefaultForm(o, request.POST)
        
        if not f.is_valid():
            if self.UseDjangoForm:
                update_dicts['form'] = str(f)
                return render_to_response(request, template, update_dicts, )
            else:
                return HttpResponse('<table>'+str(f)+'</table>') if settings.DEBUG else HttpResponseBadRequest("bad request")

        #数据合格，新增记录
        self._before_add(request)
        f.save()
        self._after_add(request, o)
        
        next_url = request.POST.get('next_url', None)
        print next_url
        if next_url:
            next_url = re.sub('{pid}', str(o.pk), next_url)
            return HttpResponseRedirect(next_url)
        
        #return HttpResponseRedirect('../'+str(o.pk)+'/')  
        return HttpResponseRedirect("../")     
    
    def _get_update_object(self, request, id):
        return self.DefaultModel.objects.get(pk = id)

    def update(self, request, template, id):
        """
        实现单一对象的更新，该方法在子类中一般不需要重写
        """ 
        o = self._get_update_object(request, id)
        if o == None:
            return HttpResponseRedirect('/')

        update_dicts = self._get_update_dicts(request, o)
        update_dicts['o'] = o
        if update_dicts.has_key("form") and isinstance(update_dicts["form"],ModelForm):
            update_dicts["form"] = self.DefaultForm(o,instance=o)
        
        if request.method == 'GET':
            if self.UseDjangoForm:
                f = self.DefaultForm(self.DefaultModel(), model_to_dict(o))
                update_dicts['form'] = str(f)
            return render_to_response(request, template, update_dicts,)
        
        if settings.DEBUG:
            print request.POST
            
        f = self.DefaultForm(o, request.POST)
        
        if not f.is_valid():
            update_dicts['form'] = str(f)
            return render_to_response(request, template, update_dicts, )
            #return HttpResponse('<table>'+str(f)+'</table>') if settings.DEBUG else HttpResponseBadRequest("bad request")
        
        #数据合格，更新记录
        f.save()
        self._after_update(request, o)
        
        next_url = request.POST.get('next_url', None)
        if next_url:
            next_url = re.sub('{pid}', str(o.pk), next_url)
            return HttpResponseRedirect(next_url)
            
        back_to_list = request.POST.get('back_to_list', None)
        if back_to_list:
            return HttpResponseRedirect('../../')
            
        
        return HttpResponseRedirect('../')


class BaseView(AbsDefaultView):
    '''新基类的雏形'''
    urlmap = {
        r'^$' : ['list', ''],
        r'^/add$' : ['add', 'update'],
        r'^/ajax_action' : ['ajax_action', ''],
        r'^/(?P<id>\d+)$' : ['view', ''],
        r'^/(?P<id>\d+)/update' : ['update', ''],
    }
    action_list = []    
    show_fields = []

    def _get_common_dicts(self,request):
        dicts = {}
        url = '/' + request.path_info.strip('/').split('/')[0]
        import re
        if re.search('BackendView$', self.__class__.__name__):
            url += '/backend'
        url += '/' + self.__class__.__name__.split('BackendView')[0].lower()
        dicts['list_url'] = url
        dicts['default_model'] = self.DefaultModel
        return dicts

    def _get_show_fields(self):
        fields = {}
        for f in self.DefaultModel._meta.fields:
            fields[f.name] = f
        show_fields = []
        for f in self.show_fields:
            if fields.has_key(f[0]):
                o = fields[f[0]]
            elif hasattr(self.DefaultModel, f[0]):
                class Obj(object):
                    pass
                o = Obj()
                o.name = f[0]
                if hasattr(self.DefaultModel,f[0]+'_name'):
                    o.verbose_name = getattr(self.DefaultModel,f[0]+'_name')
                else:
                    o.verbose_name = f[0]
            else:
                continue
            if len(f) >1:
                o.width = f[1]
            show_fields.append(o)
        return show_fields
    def _get_filter_fields(self,request):
        fields = {}
        for f in self.DefaultModel._meta.fields:
            fields[f.name] = f
        filter_fields = []
        for f in self.list_args:
            if fields.has_key(f):
                field = fields[f]
                if type(field) == 'ForeignKey':
                    choices_list = []
                    for f in field.related.parent_model.objects.all():
                        if hasattr(f,'option_text'):
                            choices_list.append((f.pk,f.option_text()))
                        else:
                            choices_list.append((f.pk,u'相应model中缺少option_text函数'))
                    field.choices_list = choices_list
                else:
                    field.choices_list = field._choices
                field.value = request.GET.get(field.name)
                filter_fields.append(fields[f])
            
        return filter_fields


    def _get_list_dicts(self, request):        
        return {}

    def _get_fields(self,form):
        fields = []
        for field in self.DefaultModel._meta.fields:
            if field.primary_key == True:
                continue
            field.type = type(field).__name__
    
            if field.type == 'ForeignKey':
                choices_list = []
                for f in field.related.parent_model.objects.all():
                    if hasattr(f,'option_text'):
                        choices_list.append((f.pk,f.option_text()))
                    else:
                        choices_list.append((f.pk,u'相应model中缺少option_text函数'))
                field.choices_list = choices_list
                if form.data.has_key(field.name+'_id'):
                    field.value = form.data[field.name+'_id']
                else:
                    field.value = ''
            else:
                field.choices_list = field._choices
                if form.data.has_key(field.name):
                    field.value = form.data[field.name]
                else:
                    field.value = ''
            field.form = form[field.name]
            fields.append(field)
        return fields

    def list(self, request, template):
        """
        实现对象的列表与查询
        """
        ls = self._get_list(request)
        dicts = self._get_common_dicts(request)
        dicts['action_list'] = self.action_list
        dicts['show_fields'] = self._get_show_fields()
        dicts['filter_fields'] = self._get_filter_fields(request)

        args = {}
        for ak in self.list_args.keys():
            if re.search('_doption$', ak):
                if request.GET.get(ak , None):
                    datestr = (request.GET.get(ak, None)).split('-')
                    args[str(self.list_args.get(ak))] = datetime.strptime((''.join((datestr[0],'-',datestr[1],'-01'))), '%Y-%m-%d')
            elif re.search('_option$', self.list_args.get(ak)):
                if request.GET.get(ak, None) and request.GET.get(ak + '_option', None):
                    args[str(ak+'__'+request.GET.get(ak + '_option', None))] = str(request.GET.get(ak, None))
            else:
                if request.GET.get(ak, None):
                    try:
                        args[str(self.list_args.get(ak))] = str(request.GET.get(ak, None))
                    except UnicodeEncodeError:
                        args[str(self.list_args.get(ak))] = request.GET.get(ak, None)
                     
        pri_contains = request.GET.get("pcontains", None)
        if pri_contains:
            ls = ls.model.objects_uc.filter_by_username_contains_pri(pri_contains, ls)
           
        pri = request.GET.get("p", None)
        if pri:    
            order = 0
            ls = ls.model.objects_uc.filter_by_jobnum_str(pri, ls, order)
            
        attstr = request.GET.get("a",None)
        if attstr: 
            order = 1           
            ls = ls.model.objects_uc.filter_by_jobnum_str(attstr, ls, order)
            
        ls = ls.filter(**args)
                
        if(request.GET.get('excel')):
            if request.method == "POST":
                cols = request.POST.getlist("cols")
                return self.csv_export(request, ls, cols)

        p = get_page(ls, request)
        obj_list = []
        for obj in p.object_list.all():
            values = []
            for field in dicts['show_fields']:
                value = getattr(obj, field.name)
                if value != None and field.__class__.__name__ == "DateField":
                    value = value.strftime("%Y-%m-%d")
                elif value!= None and field.__class__.__name__ == "DateTimeField":
                    value = value.strftime("%Y-%m-%d %H:%i:%s")
                values.append(value)
            obj_list.append((obj.pk,values))
        p.obj_list = obj_list
        c_list = []
        if self.csv_columns:
            for c in self.csv_columns:
                c_list.append(c[0].decode("utf-8"));
        dicts.update({'p':p, 'excel_cs':c_list})
        dicts.update(self._get_list_dicts(request))
        
        return render_to_response(request, template, dicts )   

    def _get_add_object(self,request):
        return {}

    def add(self, request, template):
        dicts = self._get_add_dicts(request)
        dicts.update(self._get_common_dicts(request))
        
        if request.method == 'POST':
            form = self.DefaultForm(request.POST)
            if form.is_valid():
                o = form.save()
                try:
                    o = form.save()
                except:
                    pass
                else:
                    o.save()
                    self._after_add(request, o)
                    next_url = request.GET.get('next_url')
                    if next_url:
                        return HttpResponseRedirect(next_url)
                    else:
                        path = request.path_info.strip('/').split('/')[:-1]
                        url = ''
                        for p in path:
                            url += '/' + p
                        return HttpResponseRedirect(url)
        else:
            form = self.DefaultForm()
            form.data = self._get_add_object(request)

        dicts['fields'] = self._get_fields(form)
        return render_to_response(request, template, dicts, )



    def update(self, request, template, id):
        o = self._get_update_object(request, id)
        if o == None:
            return HttpResponseRedirect('/')

        dicts = self._get_update_dicts(request)
        dicts.update(self._get_common_dicts(request))
        # dicts['o'] = o
        # if update_dicts.has_key("form") and isinstance(update_dicts["form"],ModelForm):
        #     update_dicts["form"] = self.DefaultForm(o,instance=o)
        fields = []
        if request.method == 'POST':
            form = self.DefaultForm(request.POST, instance=o)
            if form.is_valid():
                for field in o._meta.fields:
                    if not field.primary_key:
                        setattr(o,field.name,form.cleaned_data[field.name])
                o.save()
                next_url = request.POST.get('next_url', None)
                if next_url:
                    return HttpResponseRedirect(next_url)
                return HttpResponseRedirect(dicts['list_url'])
        else:
            form = self.DefaultForm()
            form.data = o

        if type(form.data) == self.DefaultModel:
            form.data = form.data.__dict__
        dicts['fields'] = self._get_fields(form)

        return render_to_response(request, template, dicts,)


    def ajax_action(self, request, template):
        ids = request.POST.getlist('id[]')
        action = request.POST.get('action')
        failed = []
        if hasattr(self, '_'+action):
            func = getattr(self,'_'+action)
            if callable(func):
                if ids:
                    for i in ids:
                        if not func(i):
                            failed.append(i)

        if len(failed) == 0:
            res = { 'next_url':'reload'}
        else:
            res = {'msg':u'操作失败，失败记录ID：' + u','.join(failed)}
        return render_to_response_json(res)

    def _delete(self, id):
        try:
            o = self.DefaultModel.objects.get(pk = id)
            o.delete()
        except:
            return False
        else:
            return True