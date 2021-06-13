from flask import Flask, request

from pv.pr_gateway.config import CONFIG as config
from pv.pr_gateway import manager
import util.proxy as proxy

app = Flask(__name__)

PR_ADDR = 'https://%s' % config['PR_ADDR']

@app.route('/str', methods=['POST'])
def post_str():
    payload = request.data
    # TODO : check outgoing payload ?
    r = proxy.post_mtls('%s/str' % PR_ADDR, payload.hex())
    # TODO : error handling ?

    return ('', r)

@app.route('/failure/<plugin_name>', methods=['POST'])
def post_failure(plugin_name):
    payload = request.json
    # TODO : check outgoing payload ?
    r = proxy.post_mtls('%s/failure/%s' % (PR_ADDR, plugin_name), payload)
    # TODO : error handling ? ex: buff the request to retry later on failure ?
    # TODO : make it async

    return ('', r)
