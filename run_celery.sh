#!/bin/sh

# wait for RabbitMQ server to start
sleep 10

cd django_celery  
# run Celery worker for our project myproject with Celery configuration stored in Celeryconf
celery worker -A  django_celery.celery -l info --autoscale=10,3