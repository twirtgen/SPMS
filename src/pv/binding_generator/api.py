import tempfile
import os

from flask import Flask, escape, jsonify, request

from  pv.binding_generator import backend as backend

app = Flask(__name__)

def format(payload):
    return (payload, 200) if payload is not None else ('', 404)

@app.route('/binding/<plugin_name>', methods=['POST'])
def get_binding(plugin_name: str):
    (fp, path) = tempfile.mkstemp(dir='/tmp')
    fp = os.fdopen(fp, 'wb')
    fp.write(request.data)
    fp.close()
    fp = open(path, 'rb')
    binding = backend.generate_binding(fp, escape(plugin_name))
    fp.close()
    os.remove(path)
    response = format(binding.read())
    binding.close()
    return response

