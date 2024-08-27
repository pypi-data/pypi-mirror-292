"""
check for duplicated initializations
"""
from textx import get_children_of_type
from virtmat.language.utilities.errors import InitializationError


def check_duplicates_processor(model, _):
    """
    processor to detect all duplicate object initializations
    """
    names = ['Variable', 'FunctionDefinition', 'ObjectImport']
    objs = []
    for name in names:
        objs.extend(get_children_of_type(name, model))
    seen = set()
    dobjs = [v for v in objs if v.name in seen or seen.add(v.name)]
    if len(dobjs) != 0:
        raise InitializationError(dobjs[0])
