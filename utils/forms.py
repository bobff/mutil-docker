#coding=utf-8
from django import forms

class Form(forms.Form):

    def save(self):
        o = self.o
        m2m_mf = [i.name for i in o._meta.many_to_many]
        m2m_ff = []
        for k in self.cleaned_data:
            if k in m2m_mf:
                m2m_ff.append(k)
                continue;
            v = self.cleaned_data[k]
            setattr(o, k, v)
        o.save()

        for k in m2m_ff:
            v = self.cleaned_data[k]
            setattr(o, k, v)

    def __init__(self, o, *args, **kwargs):
        self.o = o
        super(Form, self).__init__(*args, **kwargs)



