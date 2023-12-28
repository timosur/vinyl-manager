#!/bin/sh
set -e

# Running Migrations
echo Running Migrations.
alembic upgrade head

# Start Gunicorn processes
echo Starting Gunicorn.

gunicorn main:app --workers 2 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000