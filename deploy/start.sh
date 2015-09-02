#!/bin/sh

cd /srv/kumanodocs
gunicorn kumanodocs.wsgi:application -c deploy/gunicorn.conf.py
