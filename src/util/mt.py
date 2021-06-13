from secrets import randbits
from hashlib import sha256
from os import environ
from math import ceil

EMPTY_HASH_SIZE = environ['EMPTY_HASH_SIZE'] if 'EMPTY_HASH_SIZE' in environ else 256

# FIXME: 
#   EMPTY_HASH = bytes.fromhex(hex(randbits(EMPTY_HASH_SIZE))[2:])
#   ValueError: non-hexadecimal number found in fromhex() arg at position 63
EMPTY_HASH = bytes.fromhex(hex(randbits(EMPTY_HASH_SIZE))[2:])

class MTree:
    def __init__(self, depth: int, empty_hash=EMPTY_HASH):
        self.depth = depth
        self.leaves = {}
        self.tree = {}
        self.root = None
        self.str = None
        self.empty_hash = empty_hash

    def reset(self):
        self.leaves = {}
        self.tree = {}
        self.root = None
        self.str = None

    def set_str(self, root):
        self.str = root

    def get_str(self):
        return self.str

    def add_leaf(self, plugin: dict):
        path = path_from_name(plugin['name'], self.depth)
        try:
            self.leaves[path][plugin['name']] = plugin['binding']
        except KeyError:
            self.leaves[path] = {plugin['name']: plugin['binding']}

    def generate_tree(self):
        def iter(key: str):
            if len(key) == self.depth:
                return self.tree[key]
            h = sha256(iter('%s0' % key) + iter('%s1' % key)).digest()
            self.tree[key] = h
            return h
        self._generate_leaves()
        self.root = iter('')

    def _generate_leaves(self):
        for key in level_keys(self.depth):
            h = None
            try:
                #hashes = [sha256(plugin['binding']).digest() for plugin in self.leaves[key]]
                hashes = [sha256(binding).digest() for binding in list(self.leaves[key].values())]
                h = hashes[0] if len(hashes) == 1 else sha256(bytes.fromhex(''.join([i.hex() for i in hashes]))).digest()
            except KeyError:
                h = self.empty_hash
            self.tree[key] = h

    def _get_leaf(self, name: str, path: str) -> list:
        return self.leaves[path] if path in self.leaves and name in self.leaves[path] else None

    def get_binding(self, name: str) -> str:
        path = path_from_name(name, self.depth)
        leaf = self._get_leaf(name, path)
        return leaf[name] if leaf is not None else None

    def get_auth_nodes(self, path: str) -> list:
        l = len(path)
        return ['%s%i' % (path[:-idx], 1-int(path[l-idx])) for idx in range(1, l+1)]

    def get_auth_path(self, name: str) -> list:
        path = path_from_name(name, self.depth)
        leaf = self._get_leaf(name, path)
        result = {}
        if leaf is not None:
            if len(leaf) > 1:
                result['leaves'] = [sha256(binding).hexdigest() for pname, binding in leaf.items() if name != pname]

            for node in self.get_auth_nodes(path):
                result[node] = self.tree[node].hex()

        return result

    def dump_tree(self) -> dict:
        return {node: h.hex() for node, h in self.tree.items()}

    def dump_leaves(self) -> dict:
        return {node: {inner_node: inner_content.hex() for inner_node, inner_content in content.items()} for node, content in self.leaves.items()}

def level_keys(depth: int) -> list:
    def zero_extend(binary_string: str, depth: int) -> str:
        return '%s%s' % ('0'*(depth-len(binary_string)), binary_string)
    return [zero_extend(bin(i)[2:], depth) for i in range(0, pow(2,depth))]

def path_from_name(name: str, depth: int) -> str:
    digest = sha256(name.encode('ascii')).digest()
    return format(int(digest.hex(), 16), 'b').zfill(len(digest)*8)[:depth]
    
def proof(auth_path: dict, binding: str, root: str) -> bool:
   
    binding_hash = sha256(bytes.fromhex(binding)).digest()
    initial_hash = sha256(bytes.fromhex(''.join([binding_hash.hex()]+auth_path['leaves']))).digest() if 'leaves' in auth_path else binding_hash
    
    cumulator = initial_hash

    for node in sorted(auth_path, key=len, reverse=True):
        if node == 'leaves':
            continue
        other_hash = bytes.fromhex(auth_path[node])
        s = cumulator + other_hash if node[-1] == '1' else other_hash + cumulator
        cumulator = sha256(s).digest()

    return cumulator.hex() == root
