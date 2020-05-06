#!/bin/bash
cd /var/www/specviewer/prod/scidv_specview/
source ./venv/bin/activate
gunicorn -k gevent --workers 16 --preload --bind 0.0.0.0:5010 --timeout 60  specviewer:run_website
