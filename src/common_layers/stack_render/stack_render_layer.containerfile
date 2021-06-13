FROM python_layer

WORKDIR /cwd
RUN apk update && apk add python3 py3-pip
COPY requirements.txt .
RUN pip3 install -r requirements.txt
COPY pr.template .
COPY pv.template .
COPY stack_render.py .
ENTRYPOINT python3 stack_render.py "${1}"
