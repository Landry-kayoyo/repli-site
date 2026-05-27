#!/bin/bash
set -e

cd backend
python manage.py migrate --settings=config.settings --noinput
python manage.py collectstatic --settings=config.settings --noinput
