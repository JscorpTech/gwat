#!/bin/bash

while ! nc -z $DB_HOST $DB_PORT; do
  sleep 2
  echo "Waiting postgress...."
done

python3 manage.py collectstatic --noinput
python3 manage.py migrate --noinput

python3 manage.py events &
gunicorn config.wsgi:application -b 0.0.0.0:8000 --workers 4
exit $?
