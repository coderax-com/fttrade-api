fttrade
=======

> by Darwin Molero <darwin.molero@coderax.com>  
on Nov 6, 2024  
at Davao City, Philippines


Prep
----

$ docker-compose build

$ docker-compose up -d postgres

... wait a while for postgresql to finish launching

$ docker-compose logs postgres

... if it says `database system is ready to accept connections` we're good to go

$ docker-compose run --rm app python3 manage.py makemigrations

$ docker-compose run --rm app python3 manage.py migrate

$ docker-compose run --rm app python3 manage.py loaddata fixtures/*.json

Launch
------

$ docker-compose up -d


Tests
-----

$ docker-compose exec app python3 manage.py test


Postman
-------

I exported my collection for Postman. It is in the `postman/` directory 


Sample Transactions File
------------------------

A sample transactions file that can be used for the .csv upload 
is found in the `data-source/` directory.