#!/bin/bash

while ! nc -z $DB_HOST $DB_PORT; do
  sleep 2
  echo "$DB_HOST $DB_PORT Waiting postgress...."
done

python3 manage.py collectstatic --noinput
python3 manage.py migrate --noinput

python3 manage.py events &
celery -A config worker -l info &
celery -A config beat -l info &

gunicorn config.asgi:application -b 0.0.0.0:8000 -k uvicorn.workers.UvicornWorker
exit $?
