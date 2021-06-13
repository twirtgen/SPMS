from os import environ

import pytest

from util.binding import parse_binding

environ['VERIFIERS'] = '["P0", "P1", "P2"]'
VERIFIERS = ['P0', 'P1', 'P2']

from pv.binding_manager import api
from pv.binding_manager import config

expected_initial_db = {
            'be.qdeconinck.basic1': {'verifiers': {'P0': None, 'P1': None, 'P2': None}},
            'be.qdeconinck.basic2': {'verifiers': {'P0': None, 'P1': None, 'P2': None}},
            'be.qdeconinck.basic3': {'verifiers': {'P0': None, 'P1': None, 'P2': None}},
            'be.qdeconinck.basic4': {'verifiers': {'P0': None, 'P1': None, 'P2': None}}
        }

@pytest.fixture
def unpopulated_client():
    api.app.config['TESTING'] = True
    return api.app.test_client()

@pytest.fixture
def populated_client():
    api.app.config['TESTING'] = True
    api.backend._setup()

    #assert api.backend.bindings == expected_initial_db

    return api.app.test_client()

##### Common tests

def test_verifiers():
    assert config.VERIFIERS == VERIFIERS

def test_expression(unpopulated_client):
    with unpopulated_client as client:
        r = client.get('/internal/expression')
    assert 'P0 and P1 and P2' == r.get_json()

#### Unpopulated backend tests

def test_no_validated(unpopulated_client):
    with unpopulated_client as client:
        r = client.get('/validated')
    assert r.status_code == 404
    assert r.get_json() is None

def test_invalid_binding_id(unpopulated_client):
    with unpopulated_client as client:
        r = client.get('/binding/test')
    assert r.status_code == 404
    assert r.get_json() is None

def test_invalid_result_id(unpopulated_client):
    with unpopulated_client as client:
        r = client.post('/result/test/be.qdeconinck.basic1', json={'status': 'success'})
    assert r.status_code == 404

def test_invalid_result_binding(unpopulated_client):
    with unpopulated_client as client:
        r = client.post('/result/P0/test', json={'status': 'success'})
    assert r.status_code == 404

def test_invalid_result_payload(unpopulated_client):
    with unpopulated_client as client:
        r = client.post('/result/P0/be.qdeconinck.basic1', json=None)
        assert r.status_code == 400
        r = client.post('/result/P0/be.qdeconinck.basic1', json={})
        assert r.status_code == 400
        r = client.post('/result/P0/be.qdeconinck.basic1', json={'test': 'test'})
        assert r.status_code == 400

def test_unpopulated_internal_dabase(unpopulated_client):
    with unpopulated_client as client:
        r = client.get('/internal/database')
    assert r.status_code == 200
    assert r.get_json() == {}

#### Populated backend tests

def test_populated_internal_dabase(populated_client):
    with populated_client as client:
        r = client.get('/internal/database')
    assert r.status_code == 200
    assert r.get_json() == expected_initial_db

def test_populated_get_binding(populated_client):
    with open('tmp/binding1', 'rb') as raw_binding_fp:
            raw_binding = raw_binding_fp.read()

    for vid in VERIFIERS:
        with populated_client as client:
            r = client.get('/binding/%s' % vid)
        assert r.status_code == 200
        assert r.get_json() == parse_binding(raw_binding)

def test_populated_correct_set_result(populated_client):
    tested_plugin = 'be.qdeconinck.basic1'
    tested_verifier = 'P0'

    with populated_client as client:
        r = client.post('/result/%s/%s' % (tested_verifier, tested_plugin), json={'status': 'success'})
    assert r.status_code == 200
    
    # test the full database to search for unexpected change
    for plugin in expected_initial_db.keys():
        for vid in VERIFIERS:
            data = api.backend.bindings[plugin]['verifiers'][vid]
            assert data == {'status': 'success'} if plugin == tested_plugin and vid == tested_verifier else data is None 
