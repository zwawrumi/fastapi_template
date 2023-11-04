#!/bin/bash

alembic upgrade head

cd backend

gunicorn main:app --workers 2 --worker-class uvicorn.workers.UvicornWorker --bind=0.0.0.0:8000