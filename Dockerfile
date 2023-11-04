FROM python:3.12 as python-base

RUN mkdir app

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

ENV PYTHONPATH=/app

RUN chmod a+x docker/*.sh
#WORKDIR backend

#CMD gunicorn main:app --workers 2 --worker-class uvicorn.workers.UvicornWorker --bind=0.0.0.0:8000
