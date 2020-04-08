
FROM python:3.7

WORKDIR /usr/src/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get install -y netcat

RUN pip install --upgrade pip
COPY ./requirements.txt /usr/src/app/requirements.txt
COPY ./build/docker/services/app/scripts/entrypoint.sh /entrypoint.sh
RUN pip install -r requirements.txt

COPY ./ /usr/src/app/

ENTRYPOINT ["/entrypoint.sh"]
