FROM api_layer
WORKDIR /api

COPY pv/verifiers/terminator2/requirements.txt .
RUN pip3 install -r requirements.txt

COPY pv/verifiers/terminator2/*.py ./
COPY pv/verifiers/controller.py .
CMD PYTHONUNBUFFERED=TRUE python3 controller.py
