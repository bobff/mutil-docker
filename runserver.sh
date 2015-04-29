#!/bin/sh
min=1
max=100
while [ $min -le $max ]
do
    pid=`ps aux | grep -v 'grep' | grep 'python manage.py runserver 0.0.0.0:9999' | awk  '{print $2}' | awk 'NR==1'`
    if [ -z $pid ]; then
    echo ' '
    break
    else
    echo "kill $pid"
    sudo kill -9 $pid
    fi
done
python manage.py runserver 0.0.0.0:9999 &

min=1
max=100
while [ $min -le $max ]
do
    pid=`ps aux | grep -v 'grep' | grep 'python manage.py celery worker -B' | awk  '{print $2}' | awk 'NR==1'`
    if [ -z $pid ]; then
    echo ' '
    break
    else
    echo "kill $pid"
    sudo kill -9 $pid
    fi
done
python manage.py celery worker -B &

