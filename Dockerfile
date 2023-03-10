FROM python:3.11

WORKDIR /app

COPY requirements.txt requirements.txt
RUN  /bin/sh -c pip3 install -r requirements.txt

COPY . .











