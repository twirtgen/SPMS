from os import environ

from flask import Flask, jsonify
import requests

import util.proxy as proxy

BM_ADDR = environ['BM_ADDR'] if 'BM_ADDR' in environ else 'localhost:5000'
MT_ADDR = environ['MT_ADDR'] if 'MT_ADDR' in environ else 'localhost:4000'
MT_BASE_URL = 'http://%s/' % MT_ADDR

app = Flask(__name__)

# Merkel Tree µservice interface
@app.route('/str', methods=['GET'])
def get_str():
    return proxy.get('%sstr' % MT_BASE_URL)

@app.route('/binding/<plugin_name>', methods=['GET'])
def get_binding(plugin_name: str):
    return proxy.get('%sbinding/%s' % (MT_BASE_URL, plugin_name))

@app.route('/lookup/usr/<plugin_name>', methods=['GET'])
def get_usr_lookup(plugin_name: str):
    return proxy.get('%slookup/usr/%s' % (MT_BASE_URL, plugin_name))
