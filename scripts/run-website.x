#!/bin/bash
cd /var/www/specviewer/prod/scidb_specview/
source ./venv/bin/activate
gunicorn --workers 2 --bind 0.0.0.0:5010 --timeout 60  specviewer_website:server
