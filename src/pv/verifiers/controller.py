from json import dumps
from time import sleep
import os
import io
import tempfile
import tarfile
import shutil
import logging, logging.handlers

import requests

from verifier import verify

WAIT = 30
VERIFIER_ID = os.environ['VERIFIER_ID'] if 'VERIFIER_ID' in os.environ else ''
BM_ADDR = os.environ['BM_ADDR'] if 'BM_ADDR' in os.environ else ''
LOGGER = os.environ.get('LOGGER_ADDR', '')

http_handler = logging.handlers.HTTPHandler(LOGGER, '/log', method='POST')
http_handler.setLevel(logging.INFO)
http_handler.mapLogRecord = lambda record: {key: value for key, value in record.__dict__.items() if key in ['name', 'msg', 'levelname', 'created']};


logger = logging.getLogger('verifier.%s' % VERIFIER_ID)
logger.setLevel(logging.DEBUG)
logger.addHandler(http_handler)


while True:

    req = requests.get('http://%s/binding/%s' % (BM_ADDR, VERIFIER_ID))
    
    if req.status_code == 404:
        """ No binding available """
        # TODO: exponential backoff
        sleep(WAIT)
        continue

    if req.status_code != 200:
        # TODO : handle error
        logger.error('Got unexpected <%i> status code from the binding manager.' % req.status_code)
        continue

    """ create temporary directory in shared memory for further verifier's container """
    tmpdir = tempfile.mkdtemp(dir='/dev/shm/')

    try:
        """ get plugin data """
        plugin_code = req.content
        plugin_name = req.headers.get('X-plugin_name')
        logger.info('Processing plugin <%s>.' % plugin_name)

        """ extract plugin source code in temporary directory """
        with io.BytesIO(plugin_code) as tar_stream:
            try:
                with tarfile.open(fileobj=tar_stream, mode='r:bz2') as tar:
                    tar.extractall(path=tmpdir)
                    logger.info('* Archive extracted.')
            except tarfile.TarError as error:
                logger.error(error)

        """ call verifier on plugin's source code """
        logger.info('* Calling verifier.')
        log = verify(logger, tmpdir, plugin_name)
        result = {'status':'success'} if log is None else {'status':'failure', 'log':log}

        """ send verifier's output to binding manager """
        result_post = requests.post('http://%s/result/%s/%s' % (BM_ADDR, VERIFIER_ID, plugin_name), 
                                    headers={'Content-type':'application/json'}, data=dumps(result))
        if result_post.status_code != 200:
            # TODO : handle error
            logger.error("Unable to post verifier result to the binding manager.")
            pass
    except ValueError:
        # TODO : handle error
        pass
    finally:
        """ cleanup temporary directory """
        shutil.rmtree(tmpdir)
        logger.info('* Temporary plugin directory cleared.')
