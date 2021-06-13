from os import environ
from json import loads

RAW_VERIFIERS = environ['VERIFIERS'] if 'VERIFIERS' in environ else ''
VERIFIERS = loads(RAW_VERIFIERS) if RAW_VERIFIERS != '' else []
