#!/bin/sh

cd /srv/kumanodocs
gunicorn kumanodocs.wsgi:application -c deploy/config-files/gunicorn.conf.py
