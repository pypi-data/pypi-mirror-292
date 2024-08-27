"""type map and utility functions and classes to work with types"""
from collections.abc import Iterable
import numpy
import pandas
import pint_pandas
from fireworks.utilities.fw_serializers import FWSerializable
from virtmat.language.utilities import amml, chemistry
from virtmat.language.utilities.units import ureg
from virtmat.language.utilities.errors import RuntimeTypeError, StaticTypeError
from virtmat.language.utilities.serializable import get_serializable

typemap = {
    'Bool': bool,
    'String': str,
    'int': int,
    'float': float,
    'complex': complex,
    'Tuple': tuple,
    'Quantity': ureg.Quantity,
    'Table': pandas.DataFrame,
    'Dict': pandas.DataFrame,
    'Series': pandas.Series,
    'BoolArray': numpy.ndarray,
    'StrArray': numpy.ndarray,
    'IntArray': ureg.Quantity,
    'FloatArray': ureg.Quantity,
    'ComplexArray': ureg.Quantity,
    'IntSubArray': numpy.ndarray,
    'FloatSubArray': numpy.ndarray,
    'ComplexSubArray': numpy.ndarray,
    'AMMLStructure': amml.AMMLStructure,
    'AMMLCalculator': amml.Calculator,
    'AMMLAlgorithm': amml.Algorithm,
    'AMMLProperty': amml.Property,
    'AMMLConstraint': amml.Constraint,
    'AMMLTrajectory': amml.Trajectory,
    'AMMLNeighborList': amml.NeighborList,
    'ChemReaction': chemistry.ChemReaction,
    'ChemSpecies': chemistry.ChemSpecies
}

dtypemap = {'BoolArray': bool, 'StrArray': str, 'IntArray': int,
            'FloatArray': float, 'ComplexArray': complex, 'IntSubArray': int,
            'FloatSubArray': float, 'ComplexSubArray': complex}

scalar_realtype = (int, float, numpy.integer, numpy.floating)
scalar_numtype = (*scalar_realtype, complex, numpy.complexfloating)
scalar_booltype = (bool, numpy.bool_)
scalar_type = (str, *scalar_booltype, *scalar_numtype)


def is_numeric_type(type_):
    """check if the type_ is numeric"""
    if issubclass(type_, scalar_numtype) and not issubclass(type_, bool):
        return True
    if issubclass(type_, typemap['Quantity']):
        return True
    if issubclass(type_, numpy.ndarray) and type_.datatype in scalar_numtype:
        return True
    if issubclass(type_, typemap['Series']):
        if type_.datatype is None:
            return None
        if issubclass(type_.datatype, scalar_booltype):
            return False
        if issubclass(type_.datatype, (scalar_numtype, ureg.Quantity)):
            return True
        if issubclass(type_.datatype, numpy.ndarray):
            if type_.datatype.datatype in scalar_numtype:
                return True
    return False


def is_scalar_type(type_):
    """check if type_ is a scalar type"""
    if issubclass(type_, scalar_type):
        return True
    if issubclass(type_, ureg.Quantity) and not is_array_type(type_):
        return True
    return False


def is_array_type(type_):
    """check if type_ is array type"""
    return hasattr(type_, 'arraytype') and type_.arraytype


def is_numeric_scalar_type(type_):
    """check if the type_ is numeric scalar type"""
    return is_numeric_type(type_) and is_scalar_type(type_)


def is_numeric_array_type(type_):
    """check if the type is numeric array type"""
    return is_numeric_type(type_) and is_array_type(type_)


def is_numeric(obj):
    """check if the object is of numeric type"""
    if isinstance(obj, scalar_numtype) and not isinstance(obj, bool):
        return True
    if isinstance(obj, ureg.Quantity):
        return True
    if isinstance(obj, numpy.ndarray) and issubclass(obj.dtype.type, numpy.number):
        return True
    if isinstance(obj, pandas.Series):
        if len(obj) == 0 and isinstance(obj.dtype, pint_pandas.PintType):
            return True
        if hasattr(obj.values[0], 'magnitude'):
            return True
    if isinstance(obj, str):
        return False
    if isinstance(obj, Iterable):
        return all(is_numeric(item) for item in obj)
    return False


def is_scalar(obj):
    """check if the object is of scalar type"""
    if isinstance(obj, scalar_type):
        return True
    if isinstance(obj, ureg.Quantity) and not isinstance(obj.magnitude, numpy.ndarray):
        return True
    return False


def is_array(obj):
    """check if the obj is of an array type"""
    if isinstance(obj, numpy.ndarray):
        return True
    if isinstance(obj, ureg.Quantity) and isinstance(obj.magnitude, numpy.ndarray):
        return True
    return False


def is_numeric_scalar(obj):
    """check if the object is of numeric scalar type"""
    return is_numeric(obj) and is_scalar(obj)


def is_numeric_array(obj):
    """check if the object is of numeric array type"""
    return is_numeric(obj) and is_array(obj)


class DType(type):
    """
    A special metaclass to create types on the fly. These types (classes) have
    our specific attributes datatype and datalen.
    datatype: either a type (int, float, bool, str) or tuple of types, or None
    datalen: either an int or a tuple of ints (int instances), or None
    """
    datatype = None
    datalen = None
    arraytype = False

    def __init__(cls, *args, **kwargs):
        def new(cls, *args, **kwargs):
            base_cls = cls.__bases__[0]
            obj = base_cls.__new__(base_cls, *args, **kwargs)
            obj.__class__ = cls
            return obj
        cls.__new__ = new
        super().__init__(*args, **kwargs)

    def __eq__(cls, other):
        if other is None:  # None is abused to describe unknown type
            return cls is None
        if set(cls.__bases__) != set(other.__bases__):
            return False
        if cls.datatype is None or other.datatype is None:
            return True
        if cls.datatype != other.datatype:
            return False
        return True

    def __hash__(cls):
        return hash(repr(cls))


def checktype_(rval, type_):
    """
    Type checks at run time (dynamic type checking)
    rval: value to typecheck
    type_: bool, str or any type created with DType as metaclass
    Returns rval
    """
    if rval is not None and type_ is not None:
        try:
            if issubclass(type_, (bool, str)):
                correct_type = type_
                assert isinstance(rval, type_)
            else:
                correct_type = typemap[type_.__name__]
                # assert issubclass(type(rval), correct_type)
                assert isinstance(rval, correct_type)
        except AssertionError as err:
            msg = f'type must be {correct_type} but is {type(rval)}'
            raise RuntimeTypeError(msg) from err
        except Exception as err:
            raise err
    return rval


def checktype(func):
    """
    Type check values at run time
    func: a method of a metamodel object
    Returns: a wrapped func
    """
    def wrapper(obj):
        return checktype_(func(obj), obj.type_)
    return wrapper


def settype(func):
    """
    Adapt the type of values at run time
    func: any value function
    Returns: a wrapped func
    """
    def wrapper(*args, **kwargs):
        rval = func(*args, **kwargs)
        if isinstance(rval, bool):
            return rval
        if isinstance(rval, numpy.bool_):
            return rval.item()
        if isinstance(rval, scalar_numtype):
            return typemap['Quantity'](rval)
        if isinstance(rval, list):
            return typemap['Tuple'](rval)
        if isinstance(rval, FWSerializable) and hasattr(rval, 'to_base'):
            return rval.to_base()
        return rval
    return wrapper


def get_dfr_types(dfr):
    """return the types of the series in a dataframe"""
    dfr_types = {}
    for col in dfr.columns:
        dfr_types_set = set(type(get_serializable(e)) for e in dfr[col])
        assert len(dfr_types_set) == 1
        dfr_types[col] = next(iter(dfr_types_set))
    return dfr_types


def get_units(obj):
    """return the units of an object; if object is non-numeric return None"""
    if isinstance(obj, scalar_numtype) and not isinstance(obj, bool):
        return None
    if isinstance(obj, ureg.Quantity):
        return str(obj.units)
    if isinstance(obj, numpy.ndarray) and issubclass(obj.dtype.type, numpy.number):
        return None
    if isinstance(obj, pandas.Series):
        if len(obj) == 0 and isinstance(obj.dtype, pint_pandas.PintType):
            return str(obj.pint.units)
        if hasattr(obj.values[0], 'magnitude'):
            return str(obj.values[0].units)
    return None


specs = [
    {'typ': 'Type', 'basetype': 'Table', 'typespec': {}},
    {'typ': 'AMMLStructure', 'basetype': 'AMMLStructure', 'typespec': {'datatype': None}},
    {'typ': 'AMMLStructure', 'id': 'name', 'basetype': str},
    {'typ': 'AMMLStructure', 'id': 'atoms', 'basetype': 'Series',
     'typespec': {'datatype': ('AtomsTable', 'Table')}},
    {'typ': 'AMMLStructure', 'id': 'pbc', 'basetype': 'Series',
     'typespec': {'datatype': ('BoolArray', 'BoolArray')}},
    {'typ': 'AMMLStructure', 'id': 'cell', 'basetype': 'Series',
     'typespec': {'datatype': ('FloatArray', 'FloatArray')}},
    {'typ': 'AMMLStructure', 'id': 'kinetic_energy', 'basetype': 'Series',
     'typespec': {'datatype': float}},
    {'typ': 'AMMLStructure', 'id': 'temperature', 'basetype': 'Series',
     'typespec': {'datatype': float}},
    {'typ': 'AMMLStructure', 'id': 'distance_matrix', 'basetype': 'Series',
     'typespec': {'datatype': ('FloatArray', 'FloatArray')}},
    {'typ': 'AMMLStructure', 'id': 'chemical_formula', 'basetype': 'Series',
     'typespec': {'datatype': str}},
    {'typ': 'AMMLStructure', 'id': 'number_of_atoms', 'basetype': 'Series',
     'typespec': {'datatype': int}},
    {'typ': 'AMMLStructure', 'id': 'cell_volume', 'basetype': 'Series',
     'typespec': {'datatype': float}},
    {'typ': 'AMMLStructure', 'id': 'center_of_mass', 'basetype': 'Series',
     'typespec': {'datatype': 'FloatArray'}},
    {'typ': 'AMMLStructure', 'id': 'radius_of_gyration', 'basetype': 'Series',
     'typespec': {'datatype': float}},
    {'typ': 'AMMLStructure', 'id': 'moments_of_inertia', 'basetype': 'Series',
     'typespec': {'datatype': 'FloatArray'}},
    {'typ': 'AMMLStructure', 'id': 'angular_momentum', 'basetype': 'Series',
     'typespec': {'datatype': 'FloatArray'}},
    {'typ': 'AMMLCalculator', 'id': 'name', 'basetype': str},
    {'typ': 'AMMLCalculator', 'id': 'pinning', 'basetype': str},
    {'typ': 'AMMLCalculator', 'id': 'version', 'basetype': str},
    {'typ': 'AMMLCalculator', 'id': 'task', 'basetype': str},
    {'typ': 'AMMLCalculator', 'id': 'parameters', 'basetype': 'Table',
     'typespec': {'datatype': None}},
    {'typ': 'AMMLAlgorithm', 'id': 'name', 'basetype': str},
    {'typ': 'AMMLAlgorithm', 'id': 'parameters', 'basetype': 'Table',
     'typespec': {'datatype': None}},
    {'typ': 'AMMLProperty', 'id': 'names', 'basetype': 'Tuple',
     'typespec': {'datatype': None}},
    {'typ': 'AMMLProperty', 'id': 'calculator', 'basetype': 'AMMLCalculator',
     'typespec': {}},
    {'typ': 'AMMLProperty', 'id': 'algorithm', 'basetype': 'AMMLAlgorithm',
     'typespec': {}},
    {'typ': 'AMMLProperty', 'id': 'structure', 'basetype': 'AMMLStructure',
     'typespec': {}},
    {'typ': 'AMMLProperty', 'id': 'output_structure', 'basetype': 'AMMLStructure',
     'typespec': {}},
    {'typ': 'AMMLProperty', 'id': 'rmsd', 'basetype': 'Series',
     'typespec': {'datatype': float}},
    {'typ': 'AMMLProperty', 'id': 'forces', 'basetype': 'Series',
     'typespec': {'datatype': ('FloatArray', 'FloatArray')}},
    {'typ': 'AMMLProperty', 'id': 'dipole', 'basetype': 'Series',
     'typespec': {'datatype': ('FloatArray', 'FloatArray')}},
    {'typ': 'AMMLProperty', 'id': 'vibrational_energies', 'basetype': 'Series',
     'typespec': {'datatype': ('FloatSeries', 'Series')}},
    {'typ': 'AMMLProperty', 'id': 'energy_minimum', 'basetype': 'Series',
     'typespec': {'datatype': bool}},
    {'typ': 'AMMLProperty', 'id': 'transition_state', 'basetype': 'Series',
     'typespec': {'datatype': bool}},
    {'typ': 'AMMLProperty', 'id': 'energy', 'basetype': 'Series',
     'typespec': {'datatype': float}},
    {'typ': 'AMMLProperty', 'id': 'constraints', 'basetype': 'Tuple',
     'typespec': {'datatype': ('AMMLConstraint', 'AMMLConstraint')}},
    {'typ': 'AMMLProperty', 'id': 'results', 'basetype': 'Table',
     'typespec': {'datatype': None}},
    {'typ': 'AMMLProperty', 'id': 'rdf', 'basetype': 'Series',
     'typespec': {'datatype': ('FloatArray', 'FloatArray')}},
    {'typ': 'AMMLProperty', 'id': 'rdf_distance', 'basetype': 'Series',
     'typespec': {'datatype': ('FloatArray', 'FloatArray')}},
    {'typ': 'AMMLProperty', 'id': 'trajectory', 'basetype': 'Series',
     'typespec': {'datatype': ('AMMLTrajectory', 'AMMLTrajectory')}},
    {'typ': 'AMMLConstraint', 'basetype': 'AMMLConstraint', 'typespec': {}},
    {'typ': 'AMMLTrajectory', 'basetype': 'AMMLTrajectory', 'typespec': {}},
    {'typ': 'AMMLTrajectory', 'id': 'description', 'basetype': 'Table', 'typespec': {}},
    {'typ': 'AMMLTrajectory', 'id': 'structure', 'basetype': 'AMMLStructure', 'typespec': {}},
    {'typ': 'AMMLTrajectory', 'id': 'properties', 'basetype': 'Table', 'typespec': {}},
    {'typ': 'AMMLTrajectory', 'id': 'constraints', 'basetype': 'Series',
     'typespec': {'datatype': ('AMMLConstraint', 'AMMLConstraint')}},
    {'typ': 'AMMLTrajectory', 'id': 'filename', 'basetype': str, 'typespec': {}},
    {'typ': 'ChemSpecies', 'id': 'properties', 'basetype': 'Table', 'typespec': {}},
    {'typ': 'ChemSpecies', 'id': 'energy', 'basetype': 'Series',
     'typespec': {'datatype': float}},
    {'typ': 'ChemSpecies', 'id': 'enthalpy', 'basetype': 'Series',
     'typespec': {'datatype': float}},
    {'typ': 'ChemSpecies', 'id': 'entropy', 'basetype': 'Series',
     'typespec': {'datatype': float}},
    {'typ': 'ChemSpecies', 'id': 'free_energy', 'basetype': 'Series',
     'typespec': {'datatype': float}},
    {'typ': 'ChemSpecies', 'id': 'zpe', 'basetype': 'Series',
     'typespec': {'datatype': float}},
    {'typ': 'ChemSpecies', 'id': 'temperature', 'basetype': 'Series',
     'typespec': {'datatype': float}},
    {'typ': 'ChemSpecies', 'id': 'name', 'basetype': str},
    {'typ': 'ChemSpecies', 'id': 'composition', 'basetype': str},
    {'typ': 'ChemReaction', 'id': 'properties', 'basetype': 'Table', 'typespec': {}},
    {'typ': 'ChemReaction', 'id': 'energy', 'basetype': 'Series',
     'typespec': {'datatype': float}},
    {'typ': 'ChemReaction', 'id': 'enthalpy', 'basetype': 'Series',
     'typespec': {'datatype': float}},
    {'typ': 'ChemReaction', 'id': 'entropy', 'basetype': 'Series',
     'typespec': {'datatype': float}},
    {'typ': 'ChemReaction', 'id': 'free_energy', 'basetype': 'Series',
     'typespec': {'datatype': float}},
    {'typ': 'ChemReaction', 'id': 'zpe', 'basetype': 'Series',
     'typespec': {'datatype': float}},
    {'typ': 'ChemReaction', 'id': 'temperature', 'basetype': 'Series',
     'typespec': {'datatype': float}},
    {'typ': 'AtomsTable', 'basetype': 'Table',
     'typespec': {'datatype': None}},
    {'typ': 'BoolArray', 'basetype': 'BoolArray',
     'typespec': {'datatype': bool, 'arraytype': True}},
    {'typ': 'IntArray', 'basetype': 'IntArray',
     'typespec': {'datatype': int, 'arraytype': True}},
    {'typ': 'FloatArray', 'basetype': 'FloatArray',
     'typespec': {'datatype': float, 'arraytype': True}},
    {'typ': 'ComplexArray', 'basetype': 'ComplexArray',
     'typespec': {'datatype': complex, 'arraytype': True}},
    {'typ': 'FloatSeries', 'basetype': 'Series', 'typespec': {'datatype': float}},
    {'typ': 'Series', 'basetype': 'Series', 'typespec': {'datatype': None}},
    {'typ': 'IntSubArray', 'basetype': 'IntArray',
     'typespec': {'datatype': int, 'arraytype': True}},
    {'typ': 'FloatSubArray', 'basetype': 'FloatArray',
     'typespec': {'datatype': float, 'arraytype': True}},
    {'typ': 'ComplexSubArray', 'basetype': 'ComplexArray',
     'typespec': {'datatype': complex, 'arraytype': True}},
]


def get_dtype(typ, basetype=None, id_=None):
    """Return a DType type (class)

    Args:
        typ (str): DType name
        basetype (str): the basetype of typ if id_ is None, otherwise of attribute
        id_ (str): optional name of attribute of typ, default is None

    Returns:
        the DType type or None

    Raises:
        StaticTypeError: when DType cannot be determined
    """
    for spec in specs:
        if spec['typ'] == typ and (spec['basetype'] == basetype or spec.get('id') == id_):
            if isinstance(spec['basetype'], type):
                return spec['basetype']
            if 'datatype' in spec['typespec'] and isinstance(spec['typespec']['datatype'], tuple):
                spec['typespec']['datatype'] = get_dtype(*spec['typespec']['datatype'])
            return DType(spec['basetype'], (typemap[spec['basetype']],), spec['typespec'])
    msg = f'could not find DType for type: {typ}, basetype: {basetype}, id_: {id_}'
    raise StaticTypeError(msg)


class NotComputed:
    """Singleton that acts as placeholder not computed values"""
    _self = None

    def __new__(cls):
        if cls._self is None:
            cls._self = super().__new__(cls)
        return cls._self

    def __repr__(self):
        return 'n.c.'


NC = NotComputed()
