"""serialization/deserialization code"""
from dataclasses import dataclass
import typing
import numpy
import pandas
import pint_pandas
from pympler import asizeof
from fireworks.utilities.fw_serializers import FWSerializable
from fireworks.utilities.fw_serializers import serialize_fw
from fireworks.utilities.fw_serializers import recursive_serialize
from fireworks.utilities.fw_serializers import recursive_deserialize
from fireworks.utilities.fw_serializers import recursive_dict, load_object
from fireworks.utilities.fw_utilities import get_fw_logger
from virtmat.language.utilities import ioops, amml, chemistry
from .errors import RuntimeTypeError
from .units import ureg
from .lists import list_flatten

DATA_SCHEMA_VERSION = 5


def convert_val(number):
    """convert to native python numerical types from numpy scalar types"""
    return getattr(number, 'item', lambda: number)()


def series2dict(series):
    """convert pandas.Series with pint.Quantity to a dictionary"""
    units = [str(x.to_reduced_units().units) for x in series]
    unit = max(((u, units.count(u)) for u in set(units)), key=lambda c: c[1])[0]
    data = [get_serializable(convert_val(x.to(unit).magnitude)) for x in series]
    return {'data': data, 'name': series.name, 'units': unit}


@dataclass
class FWDataObject(FWSerializable):
    """top-level FWSerializable dataclass to hold any FWSerializable objects"""
    value: typing.Any = None
    datastore: dict = None
    filename: str = None
    _fw_name = '{{' + __loader__.name + '.' + __qualname__ + '}}'

    @serialize_fw
    @recursive_serialize
    def to_dict(self):
        if self.datastore is None:
            logger = get_fw_logger(__name__)
            mem_size = asizeof.asizeof(self.value)
            logger.debug('%s: size in memory: %s', __name__, mem_size)
            if mem_size < ioops.DATASTORE_CONFIG['inline-threshold']:
                self.datastore = {'type': None}
                return {'value': self.value, 'datastore': self.datastore}
            logger.info('%s: inline data limit exceeded: %s', __name__, mem_size)
            self.datastore, self.filename = ioops.offload_data(recursive_dict(self.value))
            if self.datastore['type'] is None:
                logger.info('%s: data not offloaded', __name__)
            else:
                logger.info('%s: data offloaded in %s', __name__, self.filename)
        if self.datastore['type'] is None:
            return {'value': self.value, 'datastore': self.datastore}
        return {'datastore': self.datastore, 'filename': self.filename}

    @classmethod
    @recursive_deserialize
    def from_dict(cls, m_dict):
        assert cls._fw_name == m_dict['_fw_name']
        if 'datastore' in m_dict and m_dict['datastore'] is not None:
            if m_dict['datastore']['type'] is None:
                return cls(m_dict['value'], m_dict['datastore'])
            assert 'filename' in m_dict and m_dict['filename'] is not None
            val = ioops.lade_data(m_dict['datastore'], m_dict['filename'])
            dval = recursive_deserialize(lambda _, x: x)(None, {'v': val})['v']
            return cls(dval, m_dict['datastore'], m_dict['filename'])
        return cls(m_dict['value'])

    @classmethod
    def from_obj(cls, obj):
        """create an instance from a serializable object of any type"""
        return cls(get_serializable(obj))


class FWDataFrame(pandas.DataFrame, FWSerializable):
    """JSON serializable pandas.DataFrame"""
    _fw_name = '{{' + __loader__.name + '.' + __qualname__ + '}}'

    def __init__(self, *args, **kwargs):
        pandas.DataFrame.__init__(self, *args, **kwargs)

    @serialize_fw
    @recursive_serialize
    def to_dict(self):
        return {'data': [get_serializable(self[c]) for c in self.columns]}

    @classmethod
    @recursive_deserialize
    def from_dict(cls, m_dict):
        assert cls._fw_name == m_dict['_fw_name']
        if len(m_dict['data']) == 0:
            return cls()
        return cls(pandas.concat(m_dict['data'], axis=1))

    def to_base(self):
        """return an instance of the base class"""
        return pandas.DataFrame(self)


class FWSeries(pandas.Series, FWSerializable):
    """JSON serializable pandas.Series"""
    _fw_name = '{{' + __loader__.name + '.' + __qualname__ + '}}'

    def __init__(self, *args, **kwargs):
        if len(args) > 0:
            if len(args[0]) == 0:
                kwargs['dtype'] = 'object'
        elif len(kwargs['data']) == 0:
            kwargs['dtype'] = 'object'
        pandas.Series.__init__(self, *args, **kwargs)

    @serialize_fw
    @recursive_serialize
    def to_dict(self):
        if isinstance(self.dtype, pint_pandas.PintType):
            return series2dict(self)
        return {'name': self.name, 'data': get_serializable(self.tolist())}

    @classmethod
    @recursive_deserialize
    def from_dict(cls, m_dict):
        assert cls._fw_name == m_dict['_fw_name']
        types = [type(elem) for elem in m_dict['data'] if elem is not None]
        if len(set(types)) > 1:
            if not all(t in (int, float) for t in types):
                msg = 'all elements in series must have the same type'
                raise RuntimeTypeError(msg)
        if float in types:
            units = m_dict.get('units', 'dimensionless')
            data = m_dict['data']
            dtype = pint_pandas.PintType(units)
        elif int in types:
            units = m_dict.get('units', 'dimensionless')
            elems = (pandas.NA if e is None else e for e in m_dict['data'])
            data = [ureg.Quantity(e, units) for e in elems]
            dtype = 'object'
        else:
            data = m_dict['data']
            dtype = None
        return cls(data=data, name=m_dict['name'], dtype=dtype)


class FWQuantity(FWSerializable, ureg.Quantity):
    """JSON serializable pint.Quantity"""
    _fw_name = '{{' + __loader__.name + '.' + __qualname__ + '}}'

    @serialize_fw
    @recursive_serialize
    def to_dict(self):
        mag, unit = self.to_tuple()
        return {'data': (get_serializable(mag), unit)}

    @classmethod
    @recursive_deserialize
    def from_dict(cls, m_dict):
        assert m_dict['_fw_name'] == cls._fw_name
        assert isinstance(m_dict['data'], (list, tuple))
        mag, unit = m_dict['data']
        if isinstance(mag, (int, float)):
            return super().from_tuple(m_dict['data'])
        if mag is None:
            return super().from_tuple((pandas.NA, unit))
        # complex encoded as a tuple of two numbers
        assert isinstance(mag, (list, tuple)) and len(mag) == 2
        return super().from_tuple((complex(*mag), unit))

    @classmethod
    def from_base(cls, obj):
        """return an instance from an instance of the base class"""
        return cls.from_tuple(obj.to_tuple())


class FWBoolArray(numpy.ndarray, FWSerializable):
    """JSON serializable bool numpy.ndarray"""
    _fw_name = '{{' + __loader__.name + '.' + __qualname__ + '}}'

    def __new__(cls, data):
        return numpy.asarray(data).view(cls)

    @serialize_fw
    @recursive_serialize
    def to_dict(self):
        return {'data': self.tolist()}

    @classmethod
    @recursive_deserialize
    def from_dict(cls, m_dict):
        assert m_dict['_fw_name'] == cls._fw_name
        assert isinstance(m_dict['data'], list)
        assert all(isinstance(e, bool) for e in list_flatten(m_dict['data']))
        return cls(m_dict['data'])


class FWStrArray(numpy.ndarray, FWSerializable):
    """JSON serializable str numpy.ndarray"""
    _fw_name = '{{' + __loader__.name + '.' + __qualname__ + '}}'

    def __new__(cls, data):
        return numpy.asarray(data).view(cls)

    @serialize_fw
    @recursive_serialize
    def to_dict(self):
        return {'data': self.tolist()}

    @classmethod
    @recursive_deserialize
    def from_dict(cls, m_dict):
        assert m_dict['_fw_name'] == cls._fw_name
        assert isinstance(m_dict['data'], list)
        assert all(isinstance(e, str) for e in list_flatten(m_dict['data']))
        return cls(m_dict['data'])


class FWNumArray(FWSerializable, ureg.Quantity):
    """JSON serializable numeric array"""
    _fw_name = '{{' + __loader__.name + '.' + __qualname__ + '}}'

    @serialize_fw
    @recursive_serialize
    def to_dict(self):
        tpl = self.to_tuple()
        return {'data': (tpl[0].tolist(), tpl[1]),
                'dtype': self.magnitude.dtype.name}

    @classmethod
    @recursive_deserialize
    def from_dict(cls, m_dict):
        assert m_dict['_fw_name'] == cls._fw_name
        array = numpy.array(m_dict['data'][0], dtype=m_dict['dtype'])
        return super().from_tuple((array, m_dict['data'][1]))

    @classmethod
    def from_base(cls, obj):
        """return an instance from an instance of the base class"""
        return cls.from_tuple(obj.to_tuple())


class FWAMMLStructure(amml.AMMLStructure, FWSerializable):
    """JSON serializable amml.AMMLStructure"""
    _fw_name = '{{' + __loader__.name + '.' + __qualname__ + '}}'

    @serialize_fw
    @recursive_serialize
    def to_dict(self):
        return {'data': get_serializable(self.tab), 'name': self.name}

    @classmethod
    @recursive_deserialize
    def from_dict(cls, m_dict):
        assert m_dict['_fw_name'] == cls._fw_name
        return cls(m_dict['data'], m_dict['name'])

    @classmethod
    def from_base(cls, obj):
        """return an instance from an instance of the base class"""
        return cls(obj.tab, obj.name)


class FWCalculator(amml.Calculator, FWSerializable):
    """JSON serializable amml.Calculator"""
    _fw_name = '{{' + __loader__.name + '.' + __qualname__ + '}}'
    _keys = ['name', 'parameters', 'pinning', 'version', 'task']

    @serialize_fw
    @recursive_serialize
    def to_dict(self):
        return {k: get_serializable(getattr(self, k)) for k in self._keys}

    @classmethod
    @recursive_deserialize
    def from_dict(cls, m_dict):
        assert cls._fw_name == m_dict.pop('_fw_name')
        return cls(**m_dict)

    @classmethod
    def from_base(cls, obj):
        """return an instance from an instance of the base class"""
        return cls(**{k: getattr(obj, k) for k in cls._keys})


class FWAlgorithm(amml.Algorithm, FWSerializable):
    """JSON serializable amml.Calculator"""
    _fw_name = '{{' + __loader__.name + '.' + __qualname__ + '}}'
    _keys = ['name', 'parameters', 'many_to_one']

    @serialize_fw
    @recursive_serialize
    def to_dict(self):
        return {k: get_serializable(getattr(self, k)) for k in self._keys}

    @classmethod
    @recursive_deserialize
    def from_dict(cls, m_dict):
        assert cls._fw_name == m_dict.pop('_fw_name')
        return cls(**m_dict)

    @classmethod
    def from_base(cls, obj):
        """return an instance from an instance of the base class"""
        return cls(**{k: getattr(obj, k) for k in cls._keys})


class FWProperty(amml.Property, FWSerializable):
    """JSON serializable amml.Property"""
    _fw_name = '{{' + __loader__.name + '.' + __qualname__ + '}}'
    _keys = ('names', 'structure', 'calculator', 'algorithm', 'constraints', 'results')

    @serialize_fw
    @recursive_serialize
    def to_dict(self):
        return {k: get_serializable(getattr(self, k)) for k in self._keys}

    @classmethod
    @recursive_deserialize
    def from_dict(cls, m_dict):
        assert cls._fw_name == m_dict.pop('_fw_name')
        return cls(**m_dict)

    @classmethod
    def from_base(cls, obj):
        """return an instance from an instance of the base class"""
        kwargs = {k: getattr(obj, k) for k in cls._keys}
        return cls(**kwargs)


class FWConstraint(amml.Constraint, FWSerializable):
    """JSON serializable amml.Constraint"""
    _fw_name = '{{' + __loader__.name + '.' + __qualname__ + '}}'

    @serialize_fw
    @recursive_serialize
    def to_dict(self):
        ser_kwargs = {k: get_serializable(v) for k, v in self.kwargs.items()}
        return {'name': self.name, **ser_kwargs}

    @classmethod
    @recursive_deserialize
    def from_dict(cls, m_dict):
        assert cls._fw_name == m_dict.pop('_fw_name')
        return cls(**m_dict)

    @classmethod
    def from_base(cls, obj):
        """return an instance from an instance of the base class"""
        return cls(obj.name, **obj.kwargs)


class FWTrajectory(amml.Trajectory, FWSerializable):
    """JSON serializable amml.Trajectory"""
    _fw_name = '{{' + __loader__.name + '.' + __qualname__ + '}}'
    _keys = ('description', 'structure', 'properties', 'constraints', 'filename')

    @serialize_fw
    @recursive_serialize
    def to_dict(self):
        return {k: get_serializable(getattr(self, k)) for k in self._keys}

    @classmethod
    @recursive_deserialize
    def from_dict(cls, m_dict):
        assert cls._fw_name == m_dict.pop('_fw_name')
        return cls(**m_dict)

    @classmethod
    def from_base(cls, obj):
        """return an instance from an instance of the base class"""
        kwargs = {k: getattr(obj, k) for k in cls._keys}
        return cls(**kwargs)


class FWChemSpecies(chemistry.ChemSpecies, FWSerializable):
    """JSON serializable chemistry.ChemSpecies"""
    _fw_name = '{{' + __loader__.name + '.' + __qualname__ + '}}'
    _keys = ['name', 'composition', 'props']

    @serialize_fw
    @recursive_serialize
    def to_dict(self):
        return {k: get_serializable(getattr(self, k)) for k in self._keys}

    @classmethod
    @recursive_deserialize
    def from_dict(cls, m_dict):
        assert cls._fw_name == m_dict.pop('_fw_name')
        return cls(**m_dict)

    @classmethod
    def from_base(cls, obj):
        """return an instance from an instance of the base class"""
        kwargs = {k: getattr(obj, k) for k in cls._keys}
        return cls(**kwargs)


class FWChemReaction(chemistry.ChemReaction, FWSerializable):
    """JSON serializable chemistry.ChemReaction"""
    _fw_name = '{{' + __loader__.name + '.' + __qualname__ + '}}'
    _keys = ['terms', 'props']

    @serialize_fw
    @recursive_serialize
    def to_dict(self):
        return {k: get_serializable(getattr(self, k)) for k in self._keys}

    @classmethod
    @recursive_deserialize
    def from_dict(cls, m_dict):
        assert cls._fw_name == m_dict.pop('_fw_name')
        return cls(**m_dict)

    @classmethod
    def from_base(cls, obj):
        """return an instance from an instance of the base class"""
        return cls(obj.terms, obj.props)


def get_serializable(obj):
    """convert an arbitrary Python object to a JSON serializable object"""
    if not isinstance(obj, FWSerializable):
        if isinstance(obj, (bool, int, float, str, type(None))):
            retval = obj
        elif isinstance(obj, (list, tuple)):
            retval = [get_serializable(o) for o in obj]
        elif isinstance(obj, dict):
            retval = {k: get_serializable(v) for k, v in obj.items()}
        elif obj is pandas.NA or obj is numpy.nan:
            retval = None
        elif isinstance(obj, complex):
            retval = (obj.real, obj.imag)
        elif isinstance(obj, ureg.Quantity):
            if isinstance(obj.magnitude, numpy.ndarray):
                retval = FWNumArray.from_base(obj)
            else:
                retval = FWQuantity.from_base(obj)
        elif isinstance(obj, pandas.DataFrame):
            retval = FWDataFrame(obj)
        elif isinstance(obj, pandas.Series):
            retval = FWSeries(obj)
        elif isinstance(obj, numpy.ndarray):
            if obj.dtype.type is numpy.bool_:
                retval = FWBoolArray(obj)
            else:
                assert obj.dtype.type is numpy.str_
                retval = FWStrArray(obj)
        elif isinstance(obj, amml.AMMLStructure):
            retval = FWAMMLStructure.from_base(obj)
        elif isinstance(obj, amml.Calculator):
            retval = FWCalculator.from_base(obj)
        elif isinstance(obj, amml.Algorithm):
            retval = FWAlgorithm.from_base(obj)
        elif isinstance(obj, amml.Property):
            retval = FWProperty.from_base(obj)
        elif isinstance(obj, amml.Constraint):
            retval = FWConstraint.from_base(obj)
        elif isinstance(obj, amml.Trajectory):
            retval = FWTrajectory.from_base(obj)
        elif isinstance(obj, chemistry.ChemSpecies):
            retval = FWChemSpecies.from_base(obj)
        elif isinstance(obj, chemistry.ChemReaction):
            retval = FWChemReaction.from_base(obj)
        else:
            raise TypeError(f'cannot serialize {obj} with type {type(obj)}')
    else:
        retval = obj
    return retval


def tag_serialize(tagtab):
    """allowed types: DataFrame, tuple / list, Quantity, bool, str"""
    assert isinstance(tagtab, pandas.DataFrame)

    def _recursive_serialize(obj):
        if isinstance(obj, pandas.DataFrame):
            out = {}
            for key, val in obj.to_dict(orient='list').items():
                assert isinstance(val, list)
                if len(val) != 1:
                    msg = f'object must have one element but has {len(val)}'
                    raise ValueError(msg)
                out[key] = _recursive_serialize(val[0])
            return out
        if isinstance(obj, ureg.Quantity):
            return get_serializable(obj).to_dict()
        if isinstance(obj, (bool, str)) or obj is None:
            return obj
        if isinstance(obj, (tuple, list)):
            return [_recursive_serialize(e) for e in obj]
        raise TypeError(f'unsupported type for query/tag: {type(obj)}')
    return _recursive_serialize(tagtab)


def tag_deserialize(tagdct):
    """deserialize a tag dict to a DataFrame object"""
    assert isinstance(tagdct, dict)

    def _recursive_deserialize(obj):
        if isinstance(obj, dict):
            if '_fw_name' in obj:
                return load_object(obj)
            dct = {k: [_recursive_deserialize(v)] for k, v in obj.items()}
            return pandas.DataFrame.from_dict(dct)
        if isinstance(obj, (bool, str)) or obj is None:
            return obj
        assert isinstance(obj, (tuple, list))
        return [_recursive_deserialize(e) for e in obj]
    return _recursive_deserialize(tagdct)
