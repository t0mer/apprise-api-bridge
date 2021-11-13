FROM techblog/fastapi:latest
LABEL maintainer="tomer.klein@gmail.com"

#install python paho-mqtt client and urllib3
RUN pip3 install apprise --no-cache-dir && \
    pip3 install pyaml --no-cache-dir


#Create working directory
RUN mkdir /opt/app

COPY app /opt/app

WORKDIR /opt/app/

EXPOSE 8080

ENTRYPOINT ["/usr/bin/python3", "app.py"]
