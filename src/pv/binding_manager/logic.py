from re import sub, fullmatch
from json import loads
from os import environ
from sys import stderr

from pv.binding_manager.config import VERIFIERS

DEFAULT_EXP = ' and '.join(VERIFIERS)

# If no expression provided, assume all properties are verified
TMP_EXP = environ['LOGICAL_EXP'] if 'LOGICAL_EXP' in environ else DEFAULT_EXP
AUTHORIZED_KEYWORDS = ['and', 'or', 'not', '(', ')']

def _valid_exp(exp: str) -> bool:
    # Extract expected identifiers by removing authorized keywords
    identifiers = [elem for elem in exp.split(' ') if elem not in AUTHORIZED_KEYWORDS]

    # Test expected identifiers against valid format
    for identifier in identifiers:
        if fullmatch('P[0-9]+', identifier) is None:
            return False

    return True

# If any expected identifier do not match the format or any element is not an authorized keyword, 
# then fallback on default logical expression
EXP = TMP_EXP if _valid_exp(TMP_EXP) else DEFAULT_EXP
formated_exp = sub('[0-9]+', r'\g<0>}', sub('P', '{', EXP))

def is_valid(values: list) -> bool:
    """
    Test a first order logic expression against a provided domain.

    The logical expression is passed as a string through the environment variable LOGICAL_EXP.

    It is then parsed to ensure its validity. If it is not valid, it falls back on a default
    expression which is the conjunction of each properties of the PV.

    Parameters
    ----------
    values
        The tested domain. The accepted values are `'True' | 'False'`

    Returns
    -------

    """
    result = False
    try:
        replaced_exp = formated_exp.format(*values)
        # FIXME : use ast.literal_eval as signaled by pylint
        result = eval(replaced_exp)
    except SyntaxError as e:
        # TODO : handle error
        print('logic.py :: %s' % e, file=stderr)

    return result

