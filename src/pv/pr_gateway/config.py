from os import environ
from json import load

def parse_env(src: dict, key: str, default):
    return src[key] if key in src else default

_env_data = {
    'PASS': '', 
    'BM_ADDR': 'pv_binding_manager_1:5000', 
    'PR_ADDR': '10.20.3.50',
    'CERT_FILE': '/dev/shm/pv.crt',
    'KEY_FILE': '/dev/shm/pv.key',
    'CA_FILE': '/dev/shm/root_ca.crt',
    'PR_PEM': '/dev/shm/pr.crt',
}

_config_data = {
        'PV_ID': '',
}

# Get config from env vars
CONFIG = {key: parse_env(environ, key, default) for key, default in _env_data.items()}

with open('pv.config', 'r') as config_fd:
    # TODO : Catch exceptions
    config = load(config_fd)

CONFIG.update({key: parse_env(config, key, default) for key, default in _config_data.items()})

VERIFIER_IDS = []
PROPERTIES = []
VERIFIERS = []

for verifier_id, metadata in config['verifiers'].items():
    if verifier_id not in VERIFIER_IDS:
        VERIFIER_IDS.append(verifier_id)

    # TODO : check config syntax
    prop = metadata['property']
    if prop not in PROPERTIES:
        PROPERTIES.append(prop)

    verifier = metadata['verifier']
    if verifier not in VERIFIERS:
        VERIFIERS.append(verifier)

CONFIG['TOPICS'] = [('verifiers/%s' % entry, 2) for entry in VERIFIERS]
CONFIG['TOPICS'] += [('properties/%s' % entry, 2) for entry in PROPERTIES]
