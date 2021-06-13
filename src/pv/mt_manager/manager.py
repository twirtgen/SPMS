from threading import Thread
from time import sleep, perf_counter
from os import environ

from readerwriterlock import rwlock
import requests

from pv.mt_manager.sign import sign, get_crt as crt
from util import mt

DEPTH = int(environ['MTDepth']) if 'MTDepth' in environ else 4
BM_ADDR = environ['BM_ADDR'] if 'BM_ADDR' in environ else 'localhost:5000'
PR_GATEWAY = environ['PR_GATEWAY'] if 'PR_GATEWAY' in environ else 'pv_pr_gateway_1'

tree = mt.MTree(DEPTH)

fair_lock = rwlock.RWLockFair()
rlock = fair_lock.gen_rlock()
wlock = fair_lock.gen_wlock()

def tree_fun(fun, *args):
    if rlock.acquire(blocking=True):
        try:
            result = (fun() if len(args) == 0 else fun(args[0])) if tree is not None else None
        finally:
            rlock.release()

    return result

def get_leaves() -> dict:
    return tree_fun(tree.dump_leaves)

def get_tree() -> dict:
    return tree_fun(tree.dump_tree)

def get_str():
    root = tree_fun(tree.get_str)
    return root.hex() if root is not None else None

def get_binding(name: str) -> bytes:
    binding = tree_fun(tree.get_binding, name)
    #return binding.hex() if binding is not None else None
    return binding

def get_auth_path(name: str) -> dict:
    path = tree_fun(tree.get_auth_path, name)
    return path if len(path) > 0 else None

def get_crt() -> str:
    return crt() 

def loop(tree):
    while True:
        # TODO : replace by next epoch wait
        sleep(10)
        req = requests.get('http://%s/validated' % BM_ADDR) 
        if req.status_code == 404:
            continue
        elif req.status_code != 200:
            # TODO: handle errors
            pass
        
        raw_bindings = req.json()
        if raw_bindings is None:
            continue 

        #plugins = {bm.extract_name(bytes.fromhex(binding)): bytes.fromhex(binding) for binding in raw_bindings}
        plugins = {name: bytes.fromhex(binding) for name, binding in raw_bindings.items()}

        # TODO : TMP DEBUG
        #print('validated plugins : %s' % ' '.join(list(plugins.keys())))

        if wlock.acquire(blocking=True):
            try:
                tree.reset()
                for pname, binding in plugins.items():
                    tree.add_leaf({'name': pname, 'binding': binding})
                begin = perf_counter()
                tree.generate_tree()
                end = perf_counter()
                tree.set_str(sign(tree.root))
                req = requests.post('http://%s/str' % PR_GATEWAY, data=tree.str)
            finally:
                wlock.release()
            
            print('perf_log, %i, %f' % (len(plugins), (end-begin)))

        # TODO : TMP DEBUG
        """
        for node, content in tree.leaves.items():
            print('%s -> %s' % (node, ' | '.join(list(content.keys()))))
        """

thread = Thread(target=loop, args=(tree,))
thread.start()
