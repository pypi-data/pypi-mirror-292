# pylint: disable = protected-access
"""Utility functions for textx"""
import re
from os import path
from textx import get_metamodel, get_model, get_location
from textx import get_children, get_parent_of_type
from textx import textx_isinstance
import virtmat

GRAMMAR_LOC = path.join(virtmat.language.__path__[0], 'grammar', 'virtmat.tx')


def isinstance_m(obj, classes):
    """
    Check whether an object is an instance of metamodel classes
    Args:
        obj: a model object
        classes: an iterable with names of classes from the metamodel
    Returns:
        True (False) if the object is (is not) instance of any class
    """
    meta = get_metamodel(obj)
    return any(textx_isinstance(obj, meta[c]) for c in classes)


def isinstance_r(obj, classes):
    """
    Check whether an instance of a class from classes is referenced in obj
    Args:
        obj: a model object
        classes: an iterable with names of classes from the metamodel
    Returns:
        True if an instance of the class is referenced, otherwise False
    """
    if hasattr(obj, 'ref'):
        ret = isinstance_r(obj.ref, classes)
    elif isinstance_m(obj, ['Variable']):
        ret = isinstance_r(obj.parameter, classes)
    else:
        ret = isinstance_m(obj, classes)
    return ret


def is_reference(obj, metamodel):
    """return True if obj is a GeneralReference"""
    return textx_isinstance(obj, metamodel['GeneralReference'])


def get_reference(obj):
    """return the referenced object if obj is a reference and obj otherwise"""
    metamodel = get_metamodel(obj)
    if is_reference(obj, metamodel):
        if textx_isinstance(obj.ref, metamodel['Variable']):
            return obj.ref.parameter
        return obj.ref
    return obj


def get_context(obj):
    """get the source code section pertinent to a textx model object obj"""
    src = getattr(get_model(obj), '_tx_model_params').get('source_code')
    beg = getattr(obj, '_tx_position')
    end = getattr(obj, '_tx_position_end')
    return None if src is None else src[beg:end].rstrip()


def get_location_context(obj):
    """get location and source code of a textx model object"""
    return {**get_location(obj), 'context': get_context(obj)}


def where_used(obj):
    """get a parent object where the object has been used"""
    stats = (('FunctionCall', 'params'), ('VarTuple', 'parameter'),
             ('Variable', 'parameter'), ('PrintParameter', 'param'))
    parents = ((get_parent_of_type(s, obj), p) for s, p in stats)
    parent, param = next((p, par) for p, par in parents if p is not None)
    if isinstance_m(parent, ['FunctionCall']):
        params = [p for p in parent.params if get_children(lambda x: x is obj, p)]
        if params:
            assert len(params) == 1
            return next(iter(params))
        return next(iter(parent.params))
    return getattr(parent, param)


def get_object_str(src, obj):
    """extract the source string of a textx object from the model string"""
    return src[obj._tx_position:obj._tx_position_end].strip()


class GrammarString:
    """create a single textX grammar string from a modular textX grammar"""
    __regex = r'^import\s+(\S+)$'

    def __init__(self, grammar_path=GRAMMAR_LOC):
        self.grammar_dir = path.dirname(grammar_path)
        self.__memo = set()
        self.__string = ''.join(self._expand_grammar(grammar_path))

    @property
    def string(self):
        """string getter"""
        return self.__string

    def _expand_grammar(self, filename):
        """recursively expand all imported grammar files without duplicates"""
        with open(filename, 'r', encoding='utf-8') as inp:
            lines = inp.readlines()
        new_lines = []
        inc_lines = []
        for line in lines:
            match = re.search(self.__regex, line)
            if match:
                include = match.group(1).replace('.', '/') + '.tx'
                if include not in self.__memo:
                    self.__memo.add(include)
                    include_file = path.join(self.grammar_dir, include)
                    inc_lines.extend(self._expand_grammar(include_file))
            else:
                new_lines.append(line)
        new_lines.extend(inc_lines)
        return new_lines
