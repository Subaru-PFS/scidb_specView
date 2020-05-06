#!/bin/bash
cd /var/www/specviewer/prod/scidb_specview/
source ./venv/bin/activate
gunicorn -k gevent --workers 10 --preload --bind 0.0.0.0:5010 --timeout 60  specviewer:website
