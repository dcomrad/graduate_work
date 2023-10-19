#!/bin/bash

set -e

while ! nc -z $ELASTIC_HOST $ELASTIC_PORT; do
  echo "Waiting for elasticsearch to start..."
  sleep 1
done
echo "Elasticsearch started"

gunicorn src.main:app --workers 4 --worker-class uvicorn.workers.UvicornH11Worker --bind 0.0.0.0:$MOVIES_PORT
