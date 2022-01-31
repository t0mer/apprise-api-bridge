FROM techblog/fastapi:latest

LABEL maintainer="tomer.klein@gmail.com"

ENV PYTHONIOENCODING=utf-8
ENV LANG=C.UTF-8

RUN apt update -yqq

RUN pip3 install apprise  --no-cache-dir && \
    pip3 install yml pyaml pyyaml --no-cache-dir


RUN mkdir /opt/app

COPY app /opt/app

WORKDIR /opt/app/

EXPOSE 8080

ENTRYPOINT ["/usr/bin/python3", "app.py"]
