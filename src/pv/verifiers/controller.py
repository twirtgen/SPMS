from json import dumps
from time import sleep
import os
import io
import tempfile
import tarfile
import shutil

from verifier import verify
import requests

WAIT = 30
VERIFIER_ID = os.environ['VERIFIER_ID'] if 'VERIFIER_ID' in os.environ else ''
BM_ADDR = os.environ['BM_ADDR'] if 'BM_ADDR' in os.environ else ''

while True:

    req = requests.get('http://%s/binding/%s' % (BM_ADDR, VERIFIER_ID))
    
    if req.status_code == 404:
        """ No binding available """
        # TODO: exponential backoff
        sleep(WAIT)
        continue

    if req.status_code != 200:
        # TODO : handle error
        print('Got unexpected <%i> status code from the binding manager.' % req.status_code)
        continue

    """ create temporary directory in shared memory for further verifier's container """
    tmpdir = tempfile.mkdtemp(dir='/dev/shm/')

    try:
        """ get plugin data """
        plugin_code = req.content
        plugin_name = req.headers.get('X-plugin_name')

        """ extract plugin source code in temporary directory """
        with io.BytesIO(plugin_code) as tar_stream:
            try:
                with tarfile.open(fileobj=tar_stream, mode='r:bz2') as tar:
                    tar.extractall(path=tmpdir)
                    print('Plugin archive extracted.')
            except tarfile.TarError as error:
                print(error)

        """ call verifier on plugin's source code """
        log = verify(tmpdir, plugin_name)
        result = {'status':'success'} if log is None else {'status':'failure', 'log':log}

        """ send verifier's output to binding manager """
        result_post = requests.post('http://%s/result/%s/%s' % (BM_ADDR, VERIFIER_ID, plugin_name), 
                                    headers={'Content-type':'application/json'}, data=dumps(result))
        if result_post.status_code != 200:
            # TODO : handle error
            print("Unable to post result")
            pass
    except ValueError:
        # TODO : handle error
        pass
    finally:
        # cleanup temporary directory
        shutil.rmtree(tmpdir)
        print('Temporary plugin directory cleared')
