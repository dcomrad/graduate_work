FROM python:3.10

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

ENV UWSGI_PROCESSES 1
ENV UWSGI_THREADS 16
ENV UWSGI_HARAKIRI 240

ENV DJANGO_SETTINGS_MODULE 'config.settings'

ENV WORKDIR /app
ENV USER web

WORKDIR $WORKDIR

COPY . .

RUN apt-get update && \
    apt-get install -y netcat-traditional && \
    pip install --upgrade pip && \
    pip install -r requirements.txt --no-cache-dir

RUN mkdir -p $WORKDIR/static/ && \
    mkdir -p $WORKDIR/media/ && \
    groupadd -r $USER && \
    useradd -d $WORKDIR -r -g $USER $USER && \
    chown $USER:$USER -R $WORKDIR && \
    chmod +x docker-entrypoint.sh

EXPOSE 8000

USER $USER

ENTRYPOINT ["./docker-entrypoint.sh"]