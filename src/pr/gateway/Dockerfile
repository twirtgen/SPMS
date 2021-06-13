FROM crypto_layer
WORKDIR /pr

COPY pr/gateway/requirements.txt .
RUN pip3 install -r requirements.txt

#COPY pr/gateway/tmp tmp

COPY pr/gateway/*.py pr/gateway/

EXPOSE 443

CMD PYTHONUNBUFFERED=TRUE gunicorn -b 0.0.0.0:443 --cert-reqs 2 --keyfile /dev/shm/key.tmp --certfile certificates/pr.pem --ca-certs certificates/root_ca.pem pr.gateway.api:app

