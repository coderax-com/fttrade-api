#!/bin/bash
#
# Make sure line endings are set to LF
#


#
# Django migrations
#
python manage.py makemigrations --no-input
python manage.py migrate --no-input


#
# create superuser
#
python manage.py createsuperuser \
    --noinput \
    --email $DJANGO_SUPERUSER_EMAIL \
    --password $DJANGO_SUPERUSER_PASSWORD


#
# cron
#
cron
tail -n 0 -f /var/log/cron.log &


#
# web app
#
python manage.py runserver 0.0.0.0:8000
