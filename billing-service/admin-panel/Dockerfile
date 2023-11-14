FROM python:3.11.6

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

ENV UWSGI_PROCESSES 1
ENV UWSGI_THREADS 16
ENV UWSGI_HARAKIRI 240

ENV DJANGO_SETTINGS_MODULE 'config.settings'

ENV WORKDIR /app
ENV USER admin

WORKDIR $WORKDIR

RUN apt-get update && \
    apt-get install -y netcat-traditional

RUN pip install --upgrade pip && \
    pip install --no-cache-dir poetry==1.4.2 && \
    poetry config virtualenvs.create false

COPY poetry.lock poetry.lock
COPY pyproject.toml pyproject.toml

RUN poetry install --without dev

COPY . .

RUN mkdir -p $WORKDIR/static/ && \
    mkdir -p $WORKDIR/media/ && \
    groupadd -r $USER && \
    useradd -d $WORKDIR -r -g $USER $USER && \
    chown $USER:$USER -R $WORKDIR && \
    chmod +x docker-entrypoint.sh

USER $USER

ENTRYPOINT ["./docker-entrypoint.sh"]