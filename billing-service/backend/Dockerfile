FROM python:3.10

ENV WORKDIR /backend
ENV USER billing

WORKDIR $WORKDIR

COPY . .

RUN apt-get update && \
    pip install --upgrade pip &&\
    apt-get install -y netcat-traditional && \
    pip install --no-cache-dir poetry==1.4.2 && \
    poetry config virtualenvs.create false && \
    poetry install --without dev

RUN groupadd -r $USER && \
    useradd -d $WORKDIR -r -g $USER $USER && \
    chown $USER:$USER -R $WORKDIR && \
    chmod +x docker-entrypoint.sh

USER $USER

EXPOSE 9900

ENTRYPOINT ["./docker-entrypoint.sh"]
