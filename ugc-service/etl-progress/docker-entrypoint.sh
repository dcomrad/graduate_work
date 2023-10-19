#!/bin/bash

set -e

while ! nc -z $KAFKA_HOST $KAFKA_PORT; do
  echo "Waiting for Kafka to start..."
  sleep 1
done
echo "Kafka started"

while ! nc -z $REDIS_HOST $REDIS_PORT; do
  echo "Waiting for Redis to start..."
  sleep 1
done
echo "Redis started"

python -m src.main
