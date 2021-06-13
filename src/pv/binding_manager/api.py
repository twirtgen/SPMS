import logging, logging.handlers
from threading import Thread
from os import environ

from flask import Flask, request, escape, jsonify, abort
import requests

from pv.binding_manager.manager import BindingBackend, UnknownId, UnknownName, ConflictingResult, MalformedPayload

# TODO : get from config
PR_GATEWAY = environ['PR_GATEWAY'] if 'PR_GATEWAY' in environ else 'pv_pr_gateway_1'
LOGGER_ADDR = environ['LOGGER_ADDR'] if 'LOGGER_ADDR' in environ else ''
BINDING_GENERATOR = environ['BINDING_GENERATOR'] if 'BINDING_GENERATOR' in environ else ''

app = Flask(__name__)

backend = BindingBackend()

# Setup HTTPHandler to forward INFO+ logs to logger µservice
# TODO : get logger addr from config
http_handler = logging.handlers.HTTPHandler(LOGGER_ADDR, '/log', method='POST')
http_handler.setLevel(logging.INFO)
http_handler.mapLogRecord = lambda record: {key: value for key, value in record.__dict__.items() if key in ['name', 'msg', 'levelname', 'created']};

# TODO : log DEBUG in /dev/shm ?

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(http_handler)

def format(payload):
    return (jsonify(payload), 200) if payload is not None else ('', 404)

@app.route('/binding/<plugin_name>', methods=['POST'])
def post_binding(plugin_name: str):
    # Get plugin code from request
    plugin_code = request.get_data()

    # Generate binding from plugin code
    binding_req = requests.post('http://%s/binding/%s' % (BINDING_GENERATOR, plugin_name), data=plugin_code)
    if binding_req.status_code != 200:
        # TODO: handle error
        return
    binding = binding_req.content

    # Add the binding in the backend and get back the plugin name
    backend.add_binding(plugin_name, plugin_code, binding)
    logger.info('post_binding : <%s>' % plugin_name)

    return ('', 200)

@app.route('/binding/<verifier_id>', methods=['GET'])
def get_binding(verifier_id):
    # Get an available binding from the backend
    binding_name, binding = backend.get_binding(escape(verifier_id)) 
    return_code = 200 if binding is not None else 404
    #result = format(binding)
    #msg = 'get_binding : <%s> : <%s>%s' % (verifier_id, result[1], ' : <%s>' % binding['name'] if result[1] == 200 else '')
    msg = 'get_binding : <%s> : <%s>%s' % (verifier_id, return_code, ' : <%s>' % binding_name if return_code == 200 else '')
    logger.log(logging.DEBUG if return_code == 404 else logging.INFO, msg)

    body = binding if binding is not None else ''
    headers = {'X-plugin_name': binding_name} if return_code == 200 else {}
    return (body, return_code, headers)

def forward_to_pr(result: dict, binding_name: str, verifier_id: str) -> None:
    try :
        if result['status'] == 'failure':
            payload = {}
            payload['log'] = result['log']
            # TODO : read verifier from PV config
            payload['verifier'] = 'tmp'
            # TODO : read PV id from PV config
            payload['pv'] = 'tmp'

            # Forward failure data to the PR_GATEWAY
            r = requests.post('http://%s/failure/%s' % (PR_GATEWAY, binding_name), json=payload)
            if r.status_code != 200:
                pass
                # TODO : handle error
    except KeyError:
        # TODO : handle error
        pass

@app.route('/result/<verifier_id>/<binding_name>', methods=['POST'])
def add_result(verifier_id, binding_name):
    try:
        result = request.json
        backend.set_result(escape(verifier_id), escape(binding_name), result)
        status = 200
        Thread(target=forward_to_pr, args=(result,binding_name,verifier_id,)).start()
    except ConflictingResult:
        status = 409
    except (UnknownName, UnknownId):
        status = 404
    except MalformedPayload:
        status = 400

    logger.log(logging.INFO if status == 200 else logging.ERROR, 'add_result : from <%s> for <%s> : status <%i>' % (verifier_id, binding_name, status))

    return ('', status)

@app.route('/validated', methods=['GET'])
def get_validated():
    return format(backend.get_validated())

@app.route('/internal/database', methods=['GET'])
def dump_database():
    return format(backend.dump_database())

@app.route('/internal/expression', methods=['GET'])
def get_expression():
    return format(backend.get_expression())
