FROM python:3.10

ENV WORKDIR /app

WORKDIR $WORKDIR

COPY . .

RUN apt-get update && \
    apt-get install -y netcat-traditional && \
    pip install --upgrade pip && \
    pip install --no-cache-dir poetry==1.4.2 && \
    poetry config virtualenvs.create false && \
    poetry install --without dev

ENTRYPOINT ["python", "rabbit_consumer.py"]