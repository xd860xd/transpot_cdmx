# Transport CDMX

Project Summary and Features
================

  + End point to see the districts (alcaldias) avaliables
  + End point to see the metrobus units
  + End point to see the request the url to get the units in one district
  + End point to get the units in one district
  + End point to get the ubication (district and address) of one metrobus unit

Usage
=================

First clone this repo and go to the project root.

    $ git clone https://github.com/xd860xd/transport_cdmx.git
    $ cd transport_cdmx

Then create the files of enviroment variables.

    $ mkdir .envs && mkdir .envs/.production && touch .envs/.production/.django && touch .envs/.production/.postgres

Now add the enviroment variables.
In .django add

    DEBUG=1
    SECRET_KEY=django-insecure-8+dqxk)mv*gz7-sw4ly@h2(%$kt@u8hxrhprc!-lr&c@!hp0ab
    CELERY_BROKER=redis://redis:6379/0
    CELERY_BACKEND=redis://redis:6379/0
    DOCKER = yes
    DJANGO_SETTINGS_MODULE = config.settings.local
    # General
    # ------------------------------------------------------------------------------
    IPYTHONDIR=/app/.ipython
    # Redis
    # ------------------------------------------------------------------------------
    REDIS_URL=redis://redis:6379/0
    # Celery
    # ------------------------------------------------------------------------------
    # Flower
    CELERY_FLOWER_USER=sjYeRSvzPyXsLEoPerLkImHuUCxSJvGL
    CELERY_FLOWER_PASSWORD=4RvvZ05xkCtOTSbw7jfbYWCgiR6ja8zWc0a8FiRq7OmJyuCJVe1N6X4pa1CiLJD8

In .postgres add:

    # PostgreSQL
    # ------------------------------------------------------------------------------
    POSTGRES_HOST=postgres
    POSTGRES_PORT=5432
    POSTGRES_DB=transport_cdmx
    POSTGRES_USER=w3484FDGDGgPLoccHdfrde
    POSTGRES_PASSWORD=QqCd3298lRFDs32eBUJnQJsA6gLQeUKfS328eDSFRFRCsDMr0r78B9dasld

***Run the project***

Run the nex commands

    $ docker-compose build
    $ docker-compose up

Try the endpoints

    http://localhost:8000/api/districts/
    http://localhost:8000/api/districts/<district>/; ex: http://localhost:8000/api/districts/Álvaro%20Obregón/ , http://localhost:8000/api/districts/Iztacalco/
    http://localhost:8000/api/units-metrobus/<id>/ ; ex: http://localhost:8000/api/units-metrobus/1/
    http://localhost:8000/api/units-metrobus/

Run tests

    $ docker-compose run --rm django python manage.py test
