FROM quay.io/keboola/docker-custom-python:latest

RUN python3 -m pip install tableauserverclient

COPY . /code/
WORKDIR /data/
CMD ["python", "-u", "/code/main.py"]
