FROM api_layer
WORKDIR /api
COPY pv/verifiers/dummy_success/* /api/
COPY pv/verifiers/controller.py /api
RUN pip3 install -r requirements.txt
CMD python3 controller.py
