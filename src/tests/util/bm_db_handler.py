from copy import deepcopy
import os

from util.binding import parse_binding
from pv.binding_manager.manager import BindingBackend, VERIFIERS

BINDINGS_DB = {}
files = os.listdir('tmp/')
files.sort()
for name in files:
    with open('tmp/%s' % name, 'rb') as binding_fd:
        binding = binding_fd.read()
        parsed = parse_binding(binding)
        BINDINGS_DB[parsed['name']] = {'binding': binding, 'verifiers': {verifier: None for verifier in VERIFIERS}}

def copy_db() -> dict:
    return deepcopy(BINDINGS_DB)

def populate(backend: BindingBackend) -> None:
    backend.bindings = deepcopy(BINDINGS_DB)

def check_db(backend: BindingBackend, expected_db: dict) -> bool:
    return backend.bindings == expected_db
