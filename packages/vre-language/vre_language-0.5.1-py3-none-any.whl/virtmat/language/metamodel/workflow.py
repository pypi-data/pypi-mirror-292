"""processors to set attributes necessary for the workflow executor"""
from textx import get_children_of_type, get_parent_of_type, textx_isinstance
from virtmat.middleware.resconfig import get_qadapter, get_worker_get_queue
from virtmat.middleware.resconfig import get_default_resconfig
from virtmat.middleware.resconfig.qadapter import get_pre_rocket
from virtmat.middleware.exceptions import ResourceConfigurationError
from virtmat.language.utilities.serializable import ureg
from virtmat.language.utilities.dupefinder import DupeFinderFunctionTask
from virtmat.language.utilities.errors import raise_exception, StaticValueError
from virtmat.language.utilities.units import norm_mem
from virtmat.language.utilities.textx import get_reference, get_object_str
from virtmat.language.utilities.logging import get_logger
from virtmat.language.constraints.units import check_number_literal_units
from virtmat.language.constraints.values import check_resources_values
from virtmat.language.constraints.values import check_resources_values_limits
from virtmat.language.constraints.values import check_number_of_chunks


def set_category(obj):
    """Set the category attribute of Resources object (obj)"""
    if obj.walltime is None:
        if obj.ncores is None:
            obj.category = 'interactive'
        else:
            if obj.ncores == 1:
                obj.category = 'interactive'
            else:
                obj.category = 'batch'
    else:
        if obj.walltime.value < ureg.Quantity(1, 'minutes'):
            if obj.ncores is not None and obj.ncores > 1:
                obj.category = 'batch'
            else:
                obj.category = 'interactive'
        else:
            obj.category = 'batch'


def set_compute_resources(obj):
    """Set resource requirements and worker_name in Resources object (obj).
    An execution model with multiple single-threaded, non-accelerated
    tasks(ranks) with balanced workload over the compute nodes is used"""
    obj.compres = {}
    obj.compres['cpus_per_task'] = 1  # currently only single-threaded supported
    if obj.walltime is not None:
        obj.compres['walltime'] = int(obj.walltime.value.to('minutes').magnitude)
    ncores = 1 if obj.ncores is None else obj.ncores
    obj.compres['ntasks'] = ncores // obj.compres['cpus_per_task']
    if obj.memory is not None:
        obj.compres['mem_per_cpu'] = obj.memory.value.to('megabyte').magnitude
    obj.wcfg, obj.qcfg = get_worker_get_queue(**obj.compres)
    obj.worker_name = obj.wcfg.name
    if obj.memory is not None:
        mem = norm_mem(obj.memory.value)
        obj.compres['mem_per_cpu'] = f'{mem[0]}{mem[1]}'


def resources_processor(obj):
    """Apply unit constraints to Resources object (obj) attributes and then set
    category and qadapter attributes in the Resources object"""
    for attr, unit in (('memory', 'bit'), ('walltime', 'second')):
        number = getattr(obj, attr)
        if number is not None:
            check_number_literal_units(number, attr, unit)
    check_resources_values(obj)
    check_resources_values_limits(obj)
    set_category(obj)
    obj.qadapter = None
    if obj.category == 'batch':
        set_compute_resources(obj)
    else:
        obj.worker_name = get_default_worker_name()


def parallelizable_processor(obj):
    """Processors for parallelizable objects"""
    check_number_of_chunks(obj)


def default_worker_name_processor(model, _):
    """set the default worker name for the model"""
    if not isinstance(model, str):
        setattr(model, 'worker_name', get_default_worker_name())


def source_code_statement_processor(model, _):
    """add source code lines pertinent to the variable objects in the model"""
    if not isinstance(model, str):
        p_src = getattr(model, '_tx_model_params').get('source_code')
        dupli = getattr(model, '_tx_model_params').get('detect_duplicates')
        for obj in get_children_of_type('Variable', model):
            vartuple_obj = get_parent_of_type('VarTuple', obj)
            var_obj = vartuple_obj if vartuple_obj else obj
            o_src = [get_object_str(p_src, var_obj)] if p_src else []
            setattr(obj, 'source_code', o_src)
            if dupli and len(o_src) > 0:
                setattr(obj, 'dupefinder', DupeFinderFunctionTask())
        for statement in ['ObjectImports', 'FunctionDefinition', 'ObjectTo']:
            for obj in get_children_of_type(statement, model):
                o_src = [get_object_str(p_src, obj)] if p_src else []
                setattr(obj, 'source_code', o_src)


def qadapter_processor(model, metamodel):
    """creates qadapter for the required resources"""
    for res in get_children_of_type('Resources', model):
        assert textx_isinstance(res.parent, metamodel['Variable'])
        if textx_isinstance(res.parent.parameter, metamodel['AMMLProperty']):
            if res.parent.parameter.calc:
                calc = get_reference(res.parent.parameter.calc)
                assert textx_isinstance(calc, metamodel['AMMLCalculator'])
                try:
                    get_pre_rocket(res.wcfg, **calc.resources)
                except ResourceConfigurationError as err:
                    raise_exception(calc, StaticValueError, str(err))
                res.compres.update(calc.resources)
        res.qadapter = get_qadapter(res.wcfg, res.qcfg, **res.compres)


def get_default_worker_name():
    """return the default worker name"""
    cfg = get_default_resconfig()
    return cfg.default_worker.name if cfg and cfg.default_worker else 'local'


def variable_update_processor(model, metamodel):
    """process variable update objects"""
    if not textx_isinstance(model, metamodel['Program']):
        return
    mod_vars = get_children_of_type('VariableUpdate', model)
    logger = get_logger(__name__)
    p_src = getattr(model, '_tx_model_params').get('source_code')
    dupli = getattr(model, '_tx_model_params').get('detect_duplicates')
    for mod_var in mod_vars:
        logger.info(' updating variable: %s', mod_var.ref.name)
        setattr(mod_var.ref, '_update', True)
        mod_var.ref.parameter = mod_var.parameter
        mod_var.ref.resources = mod_var.resources
        if p_src:
            old_src = mod_var.ref.source_code
            param_src = get_object_str(p_src, mod_var.parameter)
            new_src = f'{mod_var.ref.name} = {param_src}'
            if mod_var.resources:
                new_src = f'{new_src} {get_object_str(p_src, mod_var.resources)}'
            new_src = [new_src]
            setattr(mod_var.ref, 'source_code', new_src)
            logger.info(' updating variable source code: %s -> %s', old_src, new_src)
            if dupli:
                setattr(mod_var.ref, 'dupefinder', DupeFinderFunctionTask())
