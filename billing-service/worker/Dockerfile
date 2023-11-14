FROM python:3.10

ENV WORKDIR /app
ENV USER worker
ENV I_AM_IN_A_DOCKER_CONTAINER YES

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

RUN groupadd -r $USER && \
    useradd -d $WORKDIR -r -g $USER $USER && \
    chown $USER:$USER -R $WORKDIR && \
    chmod +x docker-entrypoint.sh

USER $USER

ENTRYPOINT ["./docker-entrypoint.sh"]