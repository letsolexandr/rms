#!/bin/bash
set -o errexit  
set -o pipefail  
set -o nounset

##INIT
python3 /opt/apps/mrs/manage.py collectstatic --noinput  
python3 /opt/apps/mrs/manage.py migrate 

gunicorn config.wsgi:application --bind 0.0.0.0:8089 --workers 8 --log-level DEBUG --access-logfile "-" --error-logfile "-"  
            
exec "$@"
