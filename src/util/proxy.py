from flask import jsonify
import requests

# TODO : handle SSL errors for PR communication

# currently if something is returned by inner services on error, it is not forwared outside
def get(url):
    req = requests.get(url)
    if req.status_code != 200:
        return ('', req.status_code)

    return (req.content, 200) if req.content is not None else ('', 200)

def post(url: str, payload):
    req = requests.post(url, json=payload)
    return ('', req.status_code)

def post_mtls(url: str, payload):
    req = requests.post(url, json=payload, cert=('/dev/shm/pv.crt', '/dev/shm/pv.key'), verify='/dev/shm/root_ca.crt')
    return req.status_code
