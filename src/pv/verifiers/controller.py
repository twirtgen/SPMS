from json import dumps
from time import sleep
import os
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
        # No binding available
        # print("No binding available")
        sleep(WAIT)
        continue

    if req.status_code != 200:
        # TODO : handle error
        continue

    # create temporary directory in shared memory for further verifier's container
    #tmpdir = tempfile.mkdtemp(dir='/dev/shm/%s' % VERIFIER_ID)
    tmpdir = '/dev/shm/%s' % VERIFIER_ID

    try:
        # get plugin data
        plugin_code = req.content
        plugin_name = req.headers.get('X-plugin_name')

        # dump plugin's code tar into file
        (fp, path) = tempfile.mkstemp(dir=tmpdir)
        fp = os.fdopen(fp, 'wb')
        fp.write(plugin_code)
        fp.close()

        # extract tar into tmpdir
        try:
            with tarfile.open(name=path, mode='r:bz2') as tar:
                tar.extractall(path=tmpdir)
        except tarfile.TarError as e:
            print(e)
        finally:
            os.remove(path)

        print('after extract')

        # call verifier on plugin's source code
        log = verify(tmpdir, plugin_name)
        result = {'status':'success'} if log is None else {'status':'failure', 'log':log}

        # send verifier's output to binding manager
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
        #shutil.rmtree(tmpdir)
        pass

