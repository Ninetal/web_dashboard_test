FROM python:3.6-slim-stretch

RUN apt-get update && apt-get install build-essential libpq-dev -y
RUN pip install --upgrade pip setuptools

COPY . /opt/web_dashboard_test/
COPY requirements.txt /tmp
RUN pip install -r /tmp/requirements.txt

WORKDIR /opt/web_dashboard_test/


