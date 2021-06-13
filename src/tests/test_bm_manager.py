from importlib import reload
from copy import deepcopy
from os import environ
import pytest
import sys

from pv.binding_manager import config, logic, manager
import tests.util.bm_db_handler as handler
from util.binding import parse_binding

VERIFIERS = ['P0', 'P1', 'P2']
SUCCESS_RESULT = {'status': 'success'}
FAILURE_RESULT = {'status': 'failure', 'log': 'my super log'}

def setup():
    environ['VERIFIERS'] = '["P0", "P1", "P2"]'
    reload(config)
    reload(manager)
    reload(logic)
    assert manager.VERIFIERS == VERIFIERS

@pytest.fixture
def empty_backend():
    setup()

    return manager.BindingBackend()

@pytest.fixture
def populated_backend():
    setup()

    backend = manager.BindingBackend()
    handler.populate(backend)
    return backend

@pytest.fixture
def second_populated_backend():
    setup()

    backend = manager.BindingBackend()
    handler.populate(backend)
    for vid in VERIFIERS:
        backend.bindings['be.qdeconinck.basic1']['verifiers'][vid] = SUCCESS_RESULT

    return backend

def test_expression(empty_backend):
    assert 'P0 and P1 and P2' == empty_backend.get_expression() 
    
    # Check that the database is left untoutched
    assert handler.check_db(empty_backend, {})

#### backend.get_binding tests

def get_binding_id(backend, vid: str, expected_db: dict) -> None:
    """ Common testing code for get_binding on empty database """
    # Check that nothing is returned
    assert backend.get_binding(vid) is None
    # Check that the database is left untouched
    assert backend.bindings == expected_db

def test_get_binding_empty_unknown_id(empty_backend):
    """ Test getting a binding for an unknown verifier id on empty database """
    get_binding_id(empty_backend, 'test', {})

def test_get_binding_populated_unknown_id(populated_backend):
    """ Test getting a binding for an unknown verifier id on populated database """
    get_binding_id(populated_backend, 'test', handler.copy_db())

def test_get_binding_empty_known_id(empty_backend):
    """ Test getting a binding for an known verifier id on empty database """
    get_binding_id(empty_backend, VERIFIERS[0], {})

def get_binding_unvalidated(backend, expected_plugin, expected_db) -> None:
    """ Common testing code for get_binding on populated db"""
    for vid in VERIFIERS:
        binding = backend.get_binding(vid)
        # Check that the returned binding is the expected format
        assert binding == parse_binding(handler.BINDINGS_DB[expected_plugin]['binding'])

    # Check that the database is left untoutched
    assert backend.bindings == expected_db

def test_get_binding_first_unvalidated(populated_backend):
    """ Test the first returned binding for each verifier when no one has been verified """
    get_binding_unvalidated(populated_backend, 'be.qdeconinck.basic1', handler.BINDINGS_DB)

def test_get_binding_second_unvalidated(second_populated_backend):
    """ Test getting the second available binding once the first one has already been verified """
    plugin = 'be.qdeconinck.basic2'
    expected_db = handler.copy_db()
    for vid in VERIFIERS:
        # Prepare expected db
        expected_db['be.qdeconinck.basic1']['verifiers'][vid] = SUCCESS_RESULT
        binding = second_populated_backend.get_binding(vid)

    get_binding_unvalidated(second_populated_backend, plugin, expected_db)

# TODO : test get_binding on fully populated db

#### backend.set_result tests

def set_result_exception(backend, vid, plugin, payload, exception, expected_db):
    with pytest.raises(exception):
        backend.set_result(vid, plugin, payload)

    # Check that the database is left untoutched
    assert backend.bindings == expected_db

def test_set_result_exception_unkown_id(empty_backend):
    """ Test setting a result for an unknown verifier id on empty database """
    set_result_exception(empty_backend, 'test', 'be.qdeconinck.basic1', SUCCESS_RESULT, manager.UnknownId, {})

def test_set_result_exception_unkown_binding(empty_backend):
    """ Test setting a result for an unknown binding on empty database """
    set_result_exception(empty_backend, VERIFIERS[0], 'test', SUCCESS_RESULT, manager.UnknownName, {})

def test_set_result_exception_conflict(second_populated_backend):
    """ Test setting a result on an already set result """
    expected_db = deepcopy(second_populated_backend.bindings)
    set_result_exception(second_populated_backend, VERIFIERS[0], 'be.qdeconinck.basic1', SUCCESS_RESULT, 
            manager.ConflictingResult, expected_db)

def test_set_result_exception_invalid_payload(populated_backend):
    """ Test setting a result with malformed payload """
    expected_db = deepcopy(populated_backend.bindings)
    set_result_exception(populated_backend, VERIFIERS[0], 'be.qdeconinck.basic1', {'test': 3}, 
            manager.MalformedPayload, expected_db)

def test_set_result_success(populated_backend):
    plugin = 'be.qdeconinck.basic1'
    result = SUCCESS_RESULT

    expected_db = handler.copy_db()
    for vid in VERIFIERS:
        # Prepare expected db
        expected_db[plugin]['verifiers'][vid] = result
        # Test setting result
        populated_backend.set_result(vid, plugin, result)
    
    # Check that the database is left untoutched
    assert populated_backend.bindings == expected_db

#### backend.get_validated tests

def test_empty_get_validated(empty_backend):
    assert empty_backend.get_validated() is None
    
    # Check that the database is left untoutched
    assert handler.check_db(empty_backend, {})

def test_first_get_validated(second_populated_backend):
    # TODO : check result
    assert second_populated_backend.get_validated() is not None

#### backend.dump_database tests

def test_initial_dump_database(populated_backend):
    assert populated_backend.dump_database() == {
            'be.qdeconinck.basic1': {'verifiers': {'P0': None, 'P1': None, 'P2': None}},
            'be.qdeconinck.basic2': {'verifiers': {'P0': None, 'P1': None, 'P2': None}},
            'be.qdeconinck.basic3': {'verifiers': {'P0': None, 'P1': None, 'P2': None}},
            'be.qdeconinck.basic4': {'verifiers': {'P0': None, 'P1': None, 'P2': None}}
        }

def test_first_set_dump_database(second_populated_backend):
    assert second_populated_backend.dump_database() == {
            'be.qdeconinck.basic1': {'verifiers': 
                {'P0': {'status': 'success'}, 'P1': {'status': 'success'}, 'P2': {'status': 'success'}}},
            'be.qdeconinck.basic2': {'verifiers': {'P0': None, 'P1': None, 'P2': None}},
            'be.qdeconinck.basic3': {'verifiers': {'P0': None, 'P1': None, 'P2': None}},
            'be.qdeconinck.basic4': {'verifiers': {'P0': None, 'P1': None, 'P2': None}}
        }
