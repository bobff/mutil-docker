# coding=utf-8
from __future__ import absolute_import

from celery import shared_task
from celery.schedules import crontab
from .models import Container
import datetime
from .views.client import Client

@shared_task
def stop_container():
	'''停止到期的容器'''
	print "stop containers "
	now = datetime.date.today()
	print now
	objs = Container.objects.filter(end_date__lt = now)
	for obj in objs:
		client = Client(obj.host_id)
		client.stop_container(obj.id)

@shared_task
def delete_container():
	'''删除过期1周的容器'''
	print "delete containers "
	one_week_ago = datetime.date.today() - datetime.timedelta(days=7)
	print one_week_ago
	objs = Container.objects.filter(end_date__lt = one_week_ago)
	for obj in objs:
		client = Client(obj.host_id)
		client.delete_container(obj.id)

