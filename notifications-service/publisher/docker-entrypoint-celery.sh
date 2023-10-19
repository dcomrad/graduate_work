#!/bin/bash

set -e

while ! nc -z $REDIS_HOST $REDIS_PORT; do
  echo "Waiting for redis to start..."
  sleep 1
done
echo "Redis started"

celery -A publisher.src.databases._celery:celery worker --loglevel=info --logfile celery.worker.log --detach
celery -A publisher.src.databases._celery:celery beat -S redbeat.RedBeatScheduler --max-interval=3 --loglevel=info --logfile celery.worker.log --detach
celery -A publisher.src.databases._celery:celery flower