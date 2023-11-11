#!/bin/bash

set -e

while ! nc -z $POSTGRES_HOST $POSTGRES_PORT; do
  echo "Waiting for postgres to start..."
  sleep 1
done
echo "Postgres started"

while ! nc -z $BACKEND_HOST $BACKEND_PORT; do
  echo "Waiting for backend to start..."
  sleep 1
done
echo "Backend started"

pytest
