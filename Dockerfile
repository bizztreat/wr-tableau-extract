FROM quay.io/keboola/docker-custom-python:latest

RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install tableauserverclient
RUN sudo apt-get -y install python3-libxml2

COPY . /code/
WORKDIR /data/
CMD ["python", "-u", "/code/main.py"]
