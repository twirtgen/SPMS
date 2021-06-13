from util.mt import MTree, proof
import pytest

mt = MTree(4, empty_hash=b'\x8ei+\xbb\xf8\xa1+\xd03\xb1D\xd1G\xa4\nZvK\xf8\x01q\x93\x9a\xc5q\xe6\xfa[\xda`\x85\xa7')
mt.add_leaf({'name': 'be.qdeconinck.basic1', 'binding': b'123450'})
mt.add_leaf({'name': 'be.qdeconinck.basic2', 'binding': b'123451'})
mt.add_leaf({'name': 'be.qdeconinck.basic3', 'binding': b'123452'})
mt.add_leaf({'name': 'be.qdeconinck.basic4', 'binding': b'123453'})


expected_tree = {
'': '8976a0733b8d95289498ea8fffab91729467d926999b4a5675bd3d3819ab2439',
'0': 'd5522d2b51dfbaf6d6e7dc273a59385df0e200230a54a753e69631ebfa38edd7',
'00': '222c705224112df4de0878deb1de255e8ed4a902bc149b62d270b530db1d5c9c',
'000': 'bc55e07a82efa5ce5fdba0813f4685829fb4f9e190bdbf3be4cb59c556db4b82',
'0000': '8e692bbbf8a12bd033b144d147a40a5a764bf80171939ac571e6fa5bda6085a7',
'0001': '8e692bbbf8a12bd033b144d147a40a5a764bf80171939ac571e6fa5bda6085a7',
'001': 'bc55e07a82efa5ce5fdba0813f4685829fb4f9e190bdbf3be4cb59c556db4b82',
'0010': '8e692bbbf8a12bd033b144d147a40a5a764bf80171939ac571e6fa5bda6085a7',
'0011': '8e692bbbf8a12bd033b144d147a40a5a764bf80171939ac571e6fa5bda6085a7',
'01': '5b98f1e4a624b2189d74966075d420234295b41e1fc55de91c154ccc8f906288',
'010': 'e46831139974df4d468e843725fa4994347d06fc78f4ef196136ea8c2760ecf1',
'0100': '5fb2f4b6da813830e17d8859070cb0ecb24907ec519a42ebb72f298a35bd459e',
'0101': '8e692bbbf8a12bd033b144d147a40a5a764bf80171939ac571e6fa5bda6085a7',
'011': 'bc55e07a82efa5ce5fdba0813f4685829fb4f9e190bdbf3be4cb59c556db4b82',
'0110': '8e692bbbf8a12bd033b144d147a40a5a764bf80171939ac571e6fa5bda6085a7',
'0111': '8e692bbbf8a12bd033b144d147a40a5a764bf80171939ac571e6fa5bda6085a7',
'1': 'e22c42012f1fa1208ecc3abc7efe0d3818d8b5b189ccb6a0ee0a7294290c4a8f',
'10': '222c705224112df4de0878deb1de255e8ed4a902bc149b62d270b530db1d5c9c',
'100': 'bc55e07a82efa5ce5fdba0813f4685829fb4f9e190bdbf3be4cb59c556db4b82',
'1000': '8e692bbbf8a12bd033b144d147a40a5a764bf80171939ac571e6fa5bda6085a7',
'1001': '8e692bbbf8a12bd033b144d147a40a5a764bf80171939ac571e6fa5bda6085a7',
'101': 'bc55e07a82efa5ce5fdba0813f4685829fb4f9e190bdbf3be4cb59c556db4b82',
'1010': '8e692bbbf8a12bd033b144d147a40a5a764bf80171939ac571e6fa5bda6085a7',
'1011': '8e692bbbf8a12bd033b144d147a40a5a764bf80171939ac571e6fa5bda6085a7',
'11': '9227eb9bbcb7c46d6dd454b3bb03ae7e69870801ad21cd8e06e0b9d170fa9327',
'110': '5902857045a93438c4bcf77294407ee4a326d6822c9885380b0f4a6a5b76fa3c',
'1100': 'dd712114fb283417de4da3512e17486adbda004060d0d1646508c8a2740d29b4',
'1101': '8e692bbbf8a12bd033b144d147a40a5a764bf80171939ac571e6fa5bda6085a7',
'111': 'd7a3faabbd124fda0db1d30877eb2abb72350140109d939fbd9eff72220d16d3',
'1110': '8e692bbbf8a12bd033b144d147a40a5a764bf80171939ac571e6fa5bda6085a7',
'1111': '77f919b0fff753c0a6169c8adfe2e7a570321d7009894d9d121ba77e2684f647',
}

def test_leaves_4():
    assert mt.leaves == {
            '0100': {'be.qdeconinck.basic1': b'123450', 'be.qdeconinck.basic3': b'123452'},
            '1100': {'be.qdeconinck.basic2': b'123451'},
            '1111': {'be.qdeconinck.basic4': b'123453'},
        }

def test_dump_leaves_4():
    assert mt.dump_leaves() == {
            '0100': {'be.qdeconinck.basic1': '313233343530', 'be.qdeconinck.basic3': '313233343532'},
            '1100': {'be.qdeconinck.basic2': '313233343531'},
            '1111': {'be.qdeconinck.basic4': '313233343533'},
        }

def test_bindings_4():
    assert mt.get_binding('be.qdeconinck.basic1') == b'123450'
    assert mt.get_binding('be.qdeconinck.basic2') == b'123451'
    assert mt.get_binding('be.qdeconinck.basic3') == b'123452'
    assert mt.get_binding('be.qdeconinck.basic4') == b'123453'
    assert mt.get_binding('be.qdeconinck.basic5') == None

def test_tree_4():
    mt.generate_tree()
    assert mt.dump_tree() == expected_tree

def test_get_str():
    assert mt.str == mt.get_str()

@pytest.mark.run(order=-1)
def test_set_str():
    mt.set_str('test_str')
    assert mt.str == 'test_str'

@pytest.mark.run(order=-2)
def test_reset():
    mt.reset()
    assert mt.leaves == {}
    assert mt.tree == {}
    assert mt.root is None
    assert mt.str is None

def test_paths_4():
    
    assert mt.get_auth_path('be.qdeconinck.basic1') == {
            '00': '222c705224112df4de0878deb1de255e8ed4a902bc149b62d270b530db1d5c9c',
            '0101': '8e692bbbf8a12bd033b144d147a40a5a764bf80171939ac571e6fa5bda6085a7',
            '011': 'bc55e07a82efa5ce5fdba0813f4685829fb4f9e190bdbf3be4cb59c556db4b82',
            '1': 'e22c42012f1fa1208ecc3abc7efe0d3818d8b5b189ccb6a0ee0a7294290c4a8f',
            'leaves': ['2d75c1a2d01521e3026aa1719256a06604e7bc99aab149cb8cc7de8552fa820d'],
        }

    assert mt.get_auth_path('be.qdeconinck.basic2') == {
            '0': 'd5522d2b51dfbaf6d6e7dc273a59385df0e200230a54a753e69631ebfa38edd7',
            '10': '222c705224112df4de0878deb1de255e8ed4a902bc149b62d270b530db1d5c9c',
            '1101': '8e692bbbf8a12bd033b144d147a40a5a764bf80171939ac571e6fa5bda6085a7',
            '111': 'd7a3faabbd124fda0db1d30877eb2abb72350140109d939fbd9eff72220d16d3',
        }

    assert mt.get_auth_path('be.qdeconinck.basic3') == {
            '00': '222c705224112df4de0878deb1de255e8ed4a902bc149b62d270b530db1d5c9c',
            '0101': '8e692bbbf8a12bd033b144d147a40a5a764bf80171939ac571e6fa5bda6085a7',
            '011': 'bc55e07a82efa5ce5fdba0813f4685829fb4f9e190bdbf3be4cb59c556db4b82',
            '1': 'e22c42012f1fa1208ecc3abc7efe0d3818d8b5b189ccb6a0ee0a7294290c4a8f',
            'leaves': ['eb76e2254ff1cb43115299491e1906fbf39921b384b983cf529ebe674d9915c1'],
        }
    
    assert mt.get_auth_path('be.qdeconinck.basic4') == {
            '0': 'd5522d2b51dfbaf6d6e7dc273a59385df0e200230a54a753e69631ebfa38edd7',
            '10': '222c705224112df4de0878deb1de255e8ed4a902bc149b62d270b530db1d5c9c',
            '110': '5902857045a93438c4bcf77294407ee4a326d6822c9885380b0f4a6a5b76fa3c',
            '1110': '8e692bbbf8a12bd033b144d147a40a5a764bf80171939ac571e6fa5bda6085a7',
        }
 
def proof_factory(name: str):
    binding = mt.get_binding(name)
    path = mt.get_auth_path(name)
    assert proof(path, binding.hex(), mt.root.hex())

def test_proofs_4():
    proof_factory('be.qdeconinck.basic1')
    proof_factory('be.qdeconinck.basic4')


