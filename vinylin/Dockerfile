FROM python:3.9.8

RUN mkdir -p /usr/src/vinylin/
WORKDIR /usr/src/vinylin/

COPY .. .

RUN apt-get update

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

EXPOSE 8000