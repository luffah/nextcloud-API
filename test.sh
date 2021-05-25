#!/bin/sh
# Script for running tests
_usage(){
  cat <<EOF
Usage : $0 [mode]
Availables modes:

 custom         (this is the default mode)
                Get environment variables for testing with an existing NextCloud instance.
                If missing, variables will be asked. Variables :
                - NEXTCLOUD_VERSION
                - NEXTCLOUD_HOSTNAME
                - NEXTCLOUD_ADMIN_USER
                - NEXTCLOUD_ADMIN_PASSWORD

 docker         Run a test-only NextCloud instance in a docker container.
                It runs following instructions.

 docker:prepare build the instance
 docker:run     run the test
 docker:end     end the instance
 
EOF
}

_get_env_vars(){
  for i in $*; do
    if [ -z "$(eval "echo \$$i")" ]; then
      printf "$i ? "
      read val
      eval "export $i=$val"
      [ "${val}" ] && continue
      echo "$i environment variable is missing.\nThe following variables are required : $*"
      exit 1
    fi
  done
}

_check_nextcloud(){
  _get_env_vars NEXTCLOUD_VERSION NEXTCLOUD_HOSTNAME NEXTCLOUD_ADMIN_USER NEXTCLOUD_ADMIN_PASSWORD
  echo "# Some modification of your instance may occur #"
  echo "Are you sure you want test the librairie with this instance ? [y/N]"
  case $(head -1) in
     y*) ;;
     *) exit 1;; 
  esac
}

_docker_compose(){ sudo docker-compose "$@"; }
(

case $1 in 
  docker)
    # _do_end=t
    if [ ! -f .test.ready ]; then
      sh $0 docker:prepare
      # _do_end=
      sleep 3
    fi
    sh $0 docker:run
    # if [ "${_to_end}" ]; then
    #   echo "== Cleaning =="
    #   sh $0 docker:end
    # fi
    ;;
  docker:prepare)
    (
    echo "== Preparing tests =="
    cd tests 
    _docker_compose up --build -d
    until _docker_compose exec --user www-data app /bin/bash -c "mkdir -p /var/www/html/custom_apps && cp -RT /tmp/groupfolders /var/www/html/custom_apps/groupfolders"; do sleep 1; done
    # sleep 10
    _docker_compose exec --user www-data app /bin/bash -c "php occ app:enable groupfolders"
    # pip3 install codecov
    touch ../.test.ready
    )
    ;;
  docker:run)
    (
    echo "== Running tests =="
    cd tests 
    # _docker_compose run --rm python-api python3 -m pytest --cov . --cov-report xml --cov-report term ..
    find . -name '*.pyc' -delete
    _docker_compose run --rm python-api python3 -m pytest ..
    )
    ;;
  docker:end)
    (
    echo "== Cleaning =="
    cd tests 
    rm ../.test.ready 2> /dev/null
    # codecov
    _docker_compose down -v
    )
    ;;
  ""|custom)
    [ -z "$NEXTCLOUD_HOSTNAME" -a -f ./.test.env ] && . ./.test.env
    _check_nextcloud
    NEXTCLOUD_HOSTNAME=$NEXTCLOUD_HOSTNAME \
      NEXTCLOUD_SSL_ENABLED=0 \
      NEXTCLOUD_ADMIN_PASSWORD=$NEXTCLOUD_ADMIN_PASSWORD \
      NEXTCLOUD_ADMIN_USER=$NEXTCLOUD_ADMIN_USER \
      NEXTCLOUD_VERSION=$NEXTCLOUD_VERSION \
      pytest .
    ;;
  *)
    _usage
    ;;
esac
)
