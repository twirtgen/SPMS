from importlib import reload
from os import environ
from re import sub

#import pv.binding_manager # setup package variables through envvars
from pv.binding_manager import config
from pv.binding_manager import logic

def gen_truth_table(n: int) -> list:
    return [i.split(',')[:-1] for i in [sub('1', 'True,', i) for i in [sub('0', 'False,', i) for i in [format(i, 'b').zfill(n) for i in range(0, pow(2,n))]]]]

def test_unique_exp():
    environ['VERIFIERS'] = '["P0"]'
    reload(config)
    reload(logic)
    
    assert logic.EXP == 'P0'
    assert logic.formated_exp == '{0}'

    assert logic.is_valid(['True'])
    assert not logic.is_valid(['False'])
    
    del environ['VERIFIERS']

def test_invalid_default_exp():
    environ['VERIFIERS'] = '["P0", "P1", "P2"]'
    environ['LOGICAL_EXP'] = 'test and P1 and P2'
    reload(config)
    reload(logic)

    assert logic.EXP == 'P0 and P1 and P2'
    
    del environ['VERIFIERS']
    del environ['LOGICAL_EXP']

def test_invalid_arg():
    environ['VERIFIERS'] = '["P0", "P1", "P2"]'
    reload(config)
    reload(logic)

    assert not logic.is_valid(['True', 'Not a bool', 'False'])
    assert not logic.is_valid(['True', 3, 'False'])
    
    del environ['VERIFIERS']

def test_valid_default_exp():
    environ['VERIFIERS'] = '["P0", "P1", "P2"]'
    reload(config)
    reload(logic)

    assert logic.EXP == 'P0 and P1 and P2'
    assert logic.formated_exp == '{0} and {1} and {2}'

    for dom in gen_truth_table(3):
        result = logic.is_valid(dom)
        assert result if dom == ['True', 'True', 'True'] else not result
   
    del environ['VERIFIERS']

def test_valid_simple_or_exp():
    environ['VERIFIERS'] = '["P0", "P1", "P2"]'
    environ['LOGICAL_EXP'] = 'P0 and P1 or P2'
    #reload(pv.binding_manager)
    reload(config)
    reload(logic)

    assert logic.DEFAULT_EXP == 'P0 and P1 and P2'
    assert logic.EXP == 'P0 and P1 or P2'
    assert logic.formated_exp == '{0} and {1} or {2}'

    for dom in gen_truth_table(3):
        result = logic.is_valid(dom)
        assert result if dom[2] == 'True' or dom[0] == dom[1] == 'True' else not result
   
    del environ['VERIFIERS']
    del environ['LOGICAL_EXP']

def test_valid_complex_exp():
    environ['VERIFIERS'] = '["P0", "P1", "P2", "P3"]'
    environ['LOGICAL_EXP'] = '( P0 and not P1 ) or not ( P2 and P3 )'
    #reload(pv.binding_manager)
    reload(config)
    reload(logic)

    assert logic.EXP == environ['LOGICAL_EXP']
    assert logic.formated_exp == '( {0} and not {1} ) or not ( {2} and {3} )'

    import sys

    for dom in gen_truth_table(4):
        result = logic.is_valid(dom)
        assert result if (dom[0] == 'True' and dom[1] == 'False') or not dom[2] == dom[3] == 'True' else not result
   
    del environ['VERIFIERS']
    del environ['LOGICAL_EXP']
