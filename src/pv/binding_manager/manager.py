from copy import deepcopy

from readerwriterlock import rwlock

from pv.binding_manager import logic
from pv.binding_manager.config import VERIFIERS

__doc__ = """This module is in charge of storing the raw bindings validated or to be validated by
the verfiers as well as their output."""

def _check_vid(verifier_id: str) -> str:
    if verifier_id not in VERIFIERS:
        # TODO : check error code
        return None
    return verifier_id

def _correct_payload_format(payload: dict) -> bool:
    try:
        keys = list(payload.keys())
    except AttributeError:
        return False

    nkeys = len(keys)
    return 'status' in keys and ((nkeys == 1 and payload['status'] == 'success') or
            (nkeys == 2 and payload['status'] == 'failure' and 'log' in keys))


class MalformedPayload(Exception):
    """ Exception raised when a received payload has an invalid format. """

class ConflictingResult(Exception):
    """ Exception raised when a result is already existing in the database. """

class UnknownName(Exception):
    """ Exception raised when the provided plugin name is not stored in the database. """

class UnknownId(Exception):
    """ Exception raised when the provided verifier id is not known by the PV. """

class BindingBackend():
    """
    Volatile in-memory bindings database for the Binding Management µservice.

    For each plugin name, it stores the raw binding as well as the output of the different
    verifiers of the PV.

    The access to the database is protected by read - write locks in order to allow
    concurrent accesses.
    """
    def __init__(self):
        self.fair_lock = rwlock.RWLockFair()
        self.rlock = self.fair_lock.gen_rlock()
        self.wlock = self.fair_lock.gen_wlock()

        self.bindings = {}
        self.expression = logic.EXP

    def _setup(self):
        ### TEMPORARY BINDING DB POPULATION
        for i in range(1,5):
            with open('tmp/binding%i' % i, mode='rb') as binding_fd:
                binding = binding_fd.read()
                self.add_binding(binding)

        for name, metadata in self.bindings.items():
            print('name %s' % name)
            print(metadata['verifiers'])
        ### END OF TEMPORARY BINDING DB POPULATION

    def get_binding(self, verifier_id: str) -> dict:
        """
        Provide the first untested binding by `verifier_id`.

        Parameters
        ----------
        verifier_id
            A valid verifier id.

        Returns
        -------
        dict
            The parsed binding if the `verifier_id` is valid.

            `None` if the `verifier_id` is unknown or if no more binding is untested.
        """
        vid = _check_vid(verifier_id)
        if vid is None:
            return None

        binding_name = ''
        binding = None
        if self.rlock.acquire(blocking=True):
            try:
                for name, metadata in self.bindings.items():
                    if metadata['verifiers'][vid] is None:
                        binding = metadata['binding']
                        binding_name = name
                        break
            finally:
                self.rlock.release()

        return (binding_name, binding)

    def set_result(self, verifier_id: str, binding_name: str, payload) -> None:
        """
        Add a verifier result in the database.

        Parameters
        ----------
        verifier_id
            The id of the verifier adding a result.

        binding_name
            The name of the binding for which `verifier_id` is adding a result.

        payload
            The result to register in the database.

        Raises
        ------
        MalformedPayload
            If the format of the payload is unexpected

        ConflictingResult
            If a result is already registered for the pair `(verifier_id, binding_name)`.

        UnknownName
            If `binding_name` is not already present in the database.

        UnknownId
            If `verifier_id` is not a valid id in this PV.
        """
        # dummy solution, takes write lock for maybe failing write
        # TODO : find better locking scheme, upgradable read lock ?
        vid = _check_vid(verifier_id)
        if vid is None:
            raise UnknownId

        if not _correct_payload_format(payload):
            raise MalformedPayload

        if self.wlock.acquire(blocking=True):
            try:
                if binding_name in self.bindings:
                    if self.bindings[binding_name]['verifiers'][vid] is None:
                        self.bindings[binding_name]['verifiers'][vid] = payload
                    else:
                        raise ConflictingResult
                else:
                    raise UnknownName
            finally:
                self.wlock.release()

    def get_validated(self) -> dict:
        """
        Get all the raw bindings validated by the PV. A binding is said validated if TODO

        See Also
        --------
        logic.is_valid
        """
        def format_entry(entry: dict) -> list:
            def convert_entry(value: dict) -> str:
                #return 'False' if value is None or value['status'] == 'failure' else 'True'
                return str(not (value is None or value['status'] == 'failure'))
            return [convert_entry(result) for result in entry.values()]

        collect = {}
        if self.rlock.acquire(blocking=True):
            try:
                for plugin_name, metadata in self.bindings.items():
                    if logic.is_valid(format_entry(metadata['verifiers'])):
                        collect[plugin_name] = metadata['tar_binding'].hex()
            finally:
                self.rlock.release()

        return collect if len(list(collect.keys())) > 0 else None

    def dump_database(self) -> dict:
        """
        Return the content of the internal database.

        Notes
        -----
        The raw bindings are removed since this function is mainly provided for debugging purpose.
        """
        result = {}
        if self.rlock.acquire(blocking=True):
            try:
                result = deepcopy(self.bindings)
            finally:
                self.rlock.release()

        # remove bindings from db copy
        for metadata in result.values():
            del metadata['binding']

        return result

    def add_binding(self, name: str, plugin_code: bytes, binding: bytes) -> None:
        """
        Adds a new raw binding.

        If an entry for the same plugin name already exists, it will override its content.

        Parameters
        ----------
        binding
            A raw bytes literal representing a binding.
        """
        if self.wlock.acquire(blocking=True):
            try:
                self.bindings[name] = {
                    'binding': plugin_code,
                    'tar_binding': binding,
                    'verifiers':{vid: None for vid in VERIFIERS}
                }
            finally:
                self.wlock.release()
        return name

    def get_expression(self) -> str:
        """
        Return the FOL expression evaluated on `get_validated` call.

        See Also
        --------
        logic.is_valid
        """
        return self.expression
