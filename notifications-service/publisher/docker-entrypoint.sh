#!/bin/bash

echo "Waiting for db ..."
while ! nc -z ${DOCKER_RABBITMQ_HOST} ${RABBITMQ_CLIENT_PORT}; do
  sleep 1
done
echo "RabbitMQ started"

echo "Running server ..."

gunicorn main:app --workers ${APP_N_WORKERS} --worker-class uvicorn.workers.UvicornWorker --bind ${APP_HOST}:${APP_PORT} --log-level debug