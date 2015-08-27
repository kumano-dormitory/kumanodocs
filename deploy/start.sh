#!/bin/sh

cd /var/lib/kumanodocs
gunicorn kumanodocs.wsgi:application -c gunicorn.conf.py
