#!/bin/bash

while ! nc -z $DB_HOST $DB_PORT; do
  sleep 2
  echo "$DB_HOST $DB_PORT Waiting postgress...."
done

python3 manage.py collectstatic --noinput
python3 manage.py migrate --noinput

# python3 manage.py events &
# uvicorn config.asgi:application --host 0.0.0.0 --port 8000 --reload --reload-dir core --reload-dir config
export PYDEVD_DISABLE_FILE_VALIDATION=1

python3 -m debugpy --listen 0.0.0.0:5678 manage.py runserver 0.0.0.0:8000

exit $?
