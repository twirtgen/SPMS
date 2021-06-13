FROM python_layer
COPY api_layer.requirements requirements.txt
RUN pip3 install -r requirements.txt
