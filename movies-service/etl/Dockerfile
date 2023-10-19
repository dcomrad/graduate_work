FROM python:3.10

ENV WORKDIR /app

WORKDIR $WORKDIR
ENV USER etl

COPY . .

RUN rm -f Dockerfile && \
    apt-get update && \
    apt-get install -y netcat-traditional && \
    pip install --upgrade pip && \
    pip install -r requirements.txt --no-cache-dir

RUN groupadd -r $USER && \
    useradd -d $WORKDIR -r -g $USER $USER && \
    chown $USER:$USER -R $WORKDIR && \
    chmod +x docker-entrypoint.sh

USER $USER

ENTRYPOINT ["./docker-entrypoint.sh"]