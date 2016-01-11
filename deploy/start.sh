#!/bin/sh

cd /srv/kumanodocs
source deploy/venv/bin/activate
gunicorn kumanodocs.wsgi:application -c deploy/config-files/gunicorn.conf.py
