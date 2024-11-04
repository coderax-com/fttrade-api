fttrade
=======


Prep
----

$ docker-compose build

$ docker-compose up -d db

$ docker-compose run --rm app python manage.py makemigrations

$ docker-compose run --rm app python manage.py migrate


Launch
------

$ docker-compose up -d
