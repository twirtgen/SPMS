FROM crypto_layer

WORKDIR /pr
RUN apk add mosquitto

COPY pr/broker/mosquitto.conf .

#COPY certificates/root_ca/root_ca.pem certificates/ca.pem
#COPY certificates/root_ca/pr.crt certificates/pr.pem

ARG KEY_FILE
ARG KEY_PASS

EXPOSE 8883

CMD mosquitto -c mosquitto.conf -v
