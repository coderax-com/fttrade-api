fttrade
=======

> by Darwin Molero <darwin.molero@coderax.com>  
on Nov 6, 2024  
at Davao City, Philippines


Prep
----

First, copy the `sample.env` as `.env`. It is in the project root directory.

    $ docker-compose build


Launch
------

    $ docker-compose up -d

... wait a while for fttrade-app to turn `Started`


Tests
-----

    $ docker-compose exec app python3 manage.py test


Postman
-------

I exported my collection for Postman. It is in the `postman/` directory.


Sample Transactions File
------------------------

A sample transactions file that can be used for the .csv upload
is found in the `data-source/` directory.


Superuser
---------

The credentials for the Django superuser:

> EMAIL = admin@fttrade.com  
PASSWORD = plsletmein
