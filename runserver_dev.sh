#!/bin/sh
pid=`ps aux | grep -v 'grep' | grep 'uwsgi uwsgi.xml' | awk  '{print $2}' | awk 'NR==1'`
sudo kill $pid
echo 'kill thread ' $pid
sudo kill $pid
echo 'kill thread ' $pid
sudo uwsgi uwsgi.xml
echo 'start uwsgi uwsgi.xml'

pid=`ps aux | grep -v 'grep' | grep '/usr/bin/python -m celery worker --logfile=/var/log/celery/worker.log --pidfile=celeryd.pid' | awk  '{print $2}' | awk 'NR==1'`
sudo kill $pid
echo 'kill thread ' $pid
pid=`ps aux | grep -v 'grep' | grep '/usr/bin/python -m celery worker --logfile=/var/log/celery/worker.log --pidfile=celeryd.pid' | awk  '{print $2}' | awk 'NR==1'`
sudo kill $pid
echo 'kill thread ' $pid
pid=`ps aux | grep -v 'grep' | grep '/usr/bin/python -m celery worker --logfile=/var/log/celery/worker.log --pidfile=celeryd.pid' | awk  '{print $2}' | awk 'NR==1'`
sudo kill $pid
echo 'kill thread ' $pid
python manage.py celery worker -D --logfile="/var/log/celery/worker.log"

pid=`ps aux | grep -v 'grep' | grep 'python manage.py celery beat --detach --logfile=/var/log/celery/beat.log' | awk  '{print $2}' | awk 'NR==1'`
sudo kill $pid
echo 'kill thread ' $pid
python manage.py celery beat --detach --logfile="/var/log/celery/beat.log"