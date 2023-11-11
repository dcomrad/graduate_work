FROM python:3.11.3

ENV WORKDIR /tests
ENV USER tests

WORKDIR $WORKDIR

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY poetry.lock poetry.lock
COPY pyproject.toml pyproject.toml

RUN apt-get update && \
    apt-get install -y netcat-traditional && \
    pip install --upgrade pip && \
    pip install --no-cache-dir poetry==1.6.1 && \
    poetry config virtualenvs.create false && \
    poetry install

COPY . .

RUN groupadd -r $USER && \
    useradd -d $WORKDIR -r -g $USER $USER && \
    chown $USER:$USER -R $WORKDIR && \
    chmod +x docker-entrypoint.sh

USER $USER

ENTRYPOINT ["./docker-entrypoint.sh"]
