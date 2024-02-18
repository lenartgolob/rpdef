# syntax=docker/dockerfile:1

FROM python:3.8-slim-buster

WORKDIR /python-docker

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .
CMD ["gunicorn", "--certfile", "fullchain.pem", "--keyfile", "privkey.pem", "--bind", "0.0.0.0:443", "app:app"]
EXPOSE 80
EXPOSE 443
EXPOSE 5000