FROM api_layer
RUN apk add python3-dev gcc musl-dev libffi-dev openssl-dev
COPY crypto_layer.requirements requirements.txt
RUN pip3 install -r requirements.txt
