#!/bin/bash
#
# Make sure line endings are set to LF
#


#
# Django migrations
#
python3 manage.py makemigrations --no-input
python3 manage.py migrate --no-input


#
# fixtures
#
python3 manage.py loaddata fixtures/*.json


#
# cron
#
cron
tail -n 0 -f /var/log/cron.log &


#
# web app
#
python manage.py runserver 0.0.0.0:8000
