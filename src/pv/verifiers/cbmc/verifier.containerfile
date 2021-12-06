FROM api_layer
WORKDIR /api

COPY pv/verifiers/cbmc/requirements.txt .
RUN pip3 install -r requirements.txt

COPY pv/verifiers/cbmc/*.py ./
COPY pv/verifiers/controller.py .

CMD PYTHONUNBUFFERED=TRUE python3 controller.py
