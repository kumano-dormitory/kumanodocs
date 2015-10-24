#!/bin/sh

cd /srv/kumanodocs/
cp db.sqlite3 deploy/backup/kumanodocs-database-backup-$(date +"%Y-%m-%d").sqlite3
