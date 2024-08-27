"""apply various constraints for literal values"""
from virtmat.middleware.resconfig import get_default_resconfig
from virtmat.language.utilities.errors import textxerror_wrap, StaticValueError


@textxerror_wrap
def check_resources_values(obj):
    """object processor to check Resources objects for general validity"""
    if obj.ncores is not None and obj.ncores < 1:
        raise StaticValueError('number of cores must be a positive integer number')
    if obj.walltime is not None and obj.walltime.value <= 0:
        raise StaticValueError('walltime must be a positive number')
    if obj.memory is not None and obj.memory.value <= 0:
        raise StaticValueError('memory must be a positive number')


@textxerror_wrap
def check_resources_values_limits(obj):
    """check whether requested resources are within the resource limits"""
    exc_list = []
    cfg = get_default_resconfig()
    if cfg is None:
        raise StaticValueError('no default resconfig found')
    for wcfg in cfg.workers:
        for qcfg in wcfg.queues:
            dct = {'worker': wcfg.name, 'queue': qcfg.name, 'exceed': []}
            max_nodes = qcfg.get_resource('nodes').maximum
            max_cpus_per_node = qcfg.get_resource('cpus_per_node').maximum
            max_walltime = qcfg.get_resource('time').maximum
            max_mem_per_cpu = qcfg.get_resource('memory_per_cpu').maximum
            max_ncores = max_nodes*max_cpus_per_node
            if obj.ncores is not None:
                if obj.ncores > max_ncores:
                    dct['exceed'].append('ncores')
            if obj.walltime is not None:
                if obj.walltime.value.to('min').magnitude > max_walltime:
                    dct['exceed'].append('walltime')
            if obj.memory is not None:
                if obj.memory.value.to('MB').magnitude > max_mem_per_cpu:
                    dct['exceed'].append('memory')
            exc_list.append(dct)
    if all(len(el['exceed']) != 0 for el in exc_list):
        raise StaticValueError(f'resource exceeds limits: {exc_list}')


@textxerror_wrap
def check_number_of_chunks(obj):
    """check number of chunks in parallelizable objects"""
    if obj.nchunks is not None and obj.nchunks < 1:
        raise StaticValueError('number of chunks must be a positive integer number')
