FROM diffblue/cbmc:5.45.0

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && \
    apt-get install -y libjson-c-dev

WORKDIR /opt
COPY cbmc.sh .

ENTRYPOINT ["/opt/cbmc.sh"]
