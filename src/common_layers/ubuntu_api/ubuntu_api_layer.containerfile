FROM ubuntu:21.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y python3 python3-pip

COPY ubuntu_api_layer.requirements requirements.txt
RUN pip3 install -r requirements.txt
