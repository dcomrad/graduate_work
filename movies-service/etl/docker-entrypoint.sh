#!/bin/bash

set -e

while ! nc -z $REDIS_HOST $REDIS_PORT; do
  echo "Waiting for Redis to start..."
  sleep 1
done
echo "Redis started"

while ! nc -z $POSTGRES_HOST $POSTGRES_PORT; do
  echo "Waiting for postgres to start..."
  sleep 1
done
echo "Postgres started"

while ! nc -z $ELASTIC_HOST $ELASTIC_PORT; do
  echo "Waiting for elasticsearch to start..."
  sleep 1
done
echo "Elasticsearch started"

python main.py