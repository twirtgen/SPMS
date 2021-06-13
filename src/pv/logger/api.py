import logging
import time
from urllib.parse import unquote

from flask import Flask, request

app = Flask(__name__)
logger = logging.getLogger('logger')
logger.setLevel('DEBUG')
handler = logging.FileHandler('pv.log')
logger.addHandler(handler)

@app.route('/log', methods=['POST'])
def post_log():
    log_data = {key: value for key, value in (record.split('=') for record in request.get_data().decode('ascii').split('&'))}
    created = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(float(log_data['created'])))
    msg = unquote(log_data['msg']).replace('+', ' ')
    log = '[%s] [%s] <%s> %s' % (created, log_data['levelname'], log_data['name'], msg)
    logger.info(log)
    print(log)

    return ('', 200)
