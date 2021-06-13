from flask import Flask, escape, jsonify

from  pv.mt_manager import manager as manager

app = Flask(__name__)

def format(payload):
    return (jsonify(payload), 200) if payload is not None else ('', 404)

@app.route('/internal/leaves', methods=['GET'])
def get_leaves():
    return format(manager.get_leaves())

@app.route('/internal/tree', methods=['GET'])
def get_tree():
    return format(manager.get_tree())

@app.route('/str', methods=['GET'])
def get_str():
    return format(manager.get_str())

@app.route('/binding/<plugin_name>', methods=['GET'])
def get_binding(plugin_name: str):
    binding = manager.get_binding(escape(plugin_name))
    return (binding, 200) if binding is not None else ('', 404)

@app.route('/lookup/usr/<plugin_name>', methods=['GET'])
def usr_lookup(plugin_name: str):
    return format(manager.get_auth_path(escape(plugin_name)))

@app.route('/crt', methods=['GET'])
def get_crt():
    return format(manager.get_crt())
