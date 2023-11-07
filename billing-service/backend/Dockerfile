FROM python:3.10

ENV WORKDIR /backend
ENV USER billing
ENV I_AM_IN_A_DOCKER_CONTAINER YES

WORKDIR $WORKDIR

COPY poetry.lock poetry.lock
COPY pyproject.toml pyproject.toml

RUN apt-get update && \
    pip install --upgrade pip &&\
    apt-get install -y netcat-traditional && \
    pip install --no-cache-dir poetry==1.4.2 && \
    poetry config virtualenvs.create false && \
    poetry install --without dev

COPY . .

RUN groupadd -r $USER && \
    useradd -d $WORKDIR -r -g $USER $USER && \
    chown $USER:$USER -R $WORKDIR && \
    chmod +x docker-entrypoint.sh

USER $USER

ENTRYPOINT ["./docker-entrypoint.sh"]
