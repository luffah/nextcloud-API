# Tests for nextcloud-API python library

Integration tests for main functionality provided by python wrapper for NextCloud API.

# How to run?

First, build, create and start containers for services in docker-compose:
    
    docker-compose up

Enable NextCloud groupfolders application:

    docker-compose exec --user www-data app /bin/bash -c \
    "cp -R /tmp/groupfolders /var/www/html/custom_apps/groupfolders && php occ app:enable groupfolders"
    
Run tests:

    docker-compose run --rm python-api python -m pytest ../
    
Run examples:

    docker-compose run --rm python-api python ../examples/user_management.py

# How to configure test container

The file `docker-compose.yml` use variables defined in the file `.env`.
Just edit this file.
