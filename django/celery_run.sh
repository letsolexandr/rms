#!/bin/sh
celery -A config worker --loglevel=INFO --concurrency 1 --without-gossip   --without-mingle --without-heartbeat --max-tasks-per-child 1