from os import listdir

from flask import Flask, request

app = Flask(__name__)

@app.route('/binding/<plugin_name>', methods=['GET'])
def get_binding(plugin_name):
    plugin = '%s.tar.bz2' % plugin_name
    if plugin not in listdir('tmp'):
        return ('', 404)

    with open('tmp/%s' % plugin, 'rb') as fd:
        content = fd.read()

    print('<%s> asked' % plugin_name) 
    return (content, 200)

@app.route('/failure/<plugin_name>', methods=['POST'])
def post_failure(plugin_name):
    if plugin_name not in listdir('tmp'):
        return ('', 404)

    print('failure received for <%s>' % plugin_name)
    print(request.json)
    return ('', 200)

@app.route('/str', methods=['POST'])
def post_str():

    print('received str')
    return ('', 200)
