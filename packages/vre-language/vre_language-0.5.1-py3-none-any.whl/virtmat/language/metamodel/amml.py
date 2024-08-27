"""processors for AMML objects"""
from virtmat.language.utilities.errors import raise_exception, StaticValueError
from virtmat.language.utilities.defparam import spec, par_units


def amml_calculator_processor(obj):
    """apply constraints to amml calculator objects"""
    if obj.name not in par_units:
        msg = f'Calculator {obj.name} is not implemented'
        raise_exception(obj, NotImplementedError, msg)
    if obj.parameters:
        par_names = obj.parameters.get_column_names()
        if not all(p in par_units[obj.name] for p in par_names):
            inv_pars = tuple(p for p in par_names if p not in par_units[obj.name])
            message = f'Invalid parameters used in calculator: {inv_pars}'
            raise_exception(obj.parameters, StaticValueError, message)
    modules = spec[obj.name].get('modulefiles') or {}
    modulefile = spec[obj.name].get('modulefile')
    if modulefile:
        ver = obj.pinning + obj.version if obj.pinning else modulefile['verspec']
        modules[modulefile['name']] = ver
    obj.resources = {'modules': modules, 'envs': spec[obj.name].get('envvars')}


def amml_algorithm_processor(obj):
    """apply constraints to amml algorithm objects"""
    if obj.name not in spec:
        msg = f'Algorithm {obj.name} is not implemented'
        raise_exception(obj, NotImplementedError, msg)
    params = spec[obj.name]['params']
    par_mandatory = [k for k, v in params.items() if 'default' not in v]
    mt1_algos = ['RDF', 'RMSD']
    if obj.many_to_one:
        if obj.name not in mt1_algos:
            msg = f'Impossible many-to-one relationship for algorithm {obj.name}'
            raise_exception(obj, StaticValueError, msg)
    if obj.parameters:
        par_names = obj.parameters.get_column_names()
        if not all(p in params for p in par_names):
            inv_pars = tuple(p for p in par_names if p not in params)
            msg = f'Invalid parameters used in algorithm {obj.name}: {inv_pars}'
            raise_exception(obj.parameters, StaticValueError, msg)
        if not all(p in par_names for p in par_mandatory):
            inv_pars = tuple(p for p in par_mandatory if p not in par_names)
            msg = f'Mandatory parameters missing in algorithm {obj.name}: {inv_pars}'
            raise_exception(obj.parameters, StaticValueError, msg)
    elif len(par_mandatory) > 0:
        msg = f'Mandatory parameters missing in algorithm {obj.name}: {par_mandatory}'
        raise_exception(obj, StaticValueError, msg)


def amml_property_processor(obj):
    """apply constraints to amml property objects"""
    calc_properties = ['energy', 'forces', 'energy_minimum',
                       'vibrational_energies']
    if obj.calc is None:
        if any(n in calc_properties for n in obj.names):
            props = tuple(n for n in obj.names if n in calc_properties)
            message = f'Need a calculator for properties {props}'
            raise_exception(obj, StaticValueError, message)


def chem_term_processor(obj):
    """replace undefined coefficients with unity by convention"""
    if obj.coefficient is None:
        obj.coefficient = 1.0
