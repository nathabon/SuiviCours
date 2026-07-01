#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input --settings=profcalendar.settings.prod

python manage.py migrate --settings=profcalendar.settings.prod

python manage.py create_admin --settings=profcalendar.settings.prod