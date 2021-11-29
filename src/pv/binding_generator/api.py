import tempfile
import os

from flask import Flask, escape, jsonify, request

from pv.binding_generator import generate_binding

app = Flask(__name__)

def format(payload):
    return (payload, 200) if payload is not None else ('', 404)

@app.route('/binding/<plugin_name>', methods=['POST'])
def get_binding(plugin_name: str):
    return format(generate_binding(request.data, escape(plugin_name)))
