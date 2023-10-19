#!/bin/bash

set -e

while ! nc -z $KAFKA_HOST $KAFKA_PORT; do
  echo "Waiting for kafka to start..."
  sleep 1
done
echo "Kafka started"

while ! nc -z $REDIS_HOST $REDIS_PORT; do
  echo "Waiting for redis to start..."
  sleep 1
done
echo "Redis started"

gunicorn src.main:app --workers 4 --worker-class uvicorn.workers.UvicornH11Worker --bind 0.0.0.0:$UGC_PORT
