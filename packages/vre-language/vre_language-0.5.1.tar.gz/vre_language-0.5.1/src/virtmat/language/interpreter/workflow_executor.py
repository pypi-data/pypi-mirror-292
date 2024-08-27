# pylint: disable = protected-access
"""
Language interpreter for distributed/remote evaluation using workflow
management systems and batch systems.

Variables store outputs of function tasks, therefore a variable is in the root
of every evaluation (-> mapped to a task in the workflow). Grouping tasks to
nodes can be done either via simple mapping line of code -> node, or based on
graph analysis.
"""
import base64
import traceback
import uuid
from functools import cached_property
import dill
import pandas
from textx import get_children_of_type, get_children, get_model
from textx.exceptions import TextXError
from fireworks import Firework, Workflow
from virtmat.language.utilities.firetasks import FunctionTask, ExportDataTask, ScatterTask
from virtmat.language.utilities.fireworks import run_fireworks, get_ancestors
from virtmat.language.utilities.fireworks import get_nodes_providing, get_parent_nodes
from virtmat.language.utilities.fireworks import safe_update, get_nodes_info, retrieve_value
from virtmat.language.utilities.serializable import DATA_SCHEMA_VERSION
from virtmat.language.utilities.serializable import FWDataObject, tag_serialize
from virtmat.language.utilities.textx import isinstance_m
from virtmat.language.utilities.formatters import formatter
from virtmat.language.utilities.errors import textxerror_wrap, error_handler
from virtmat.language.utilities.errors import EvaluationError, AncestorEvaluationError
from virtmat.language.utilities.errors import TEXTX_WRAPPED_EXCEPTIONS, NonCompletedException
from virtmat.language.utilities.types import checktype, settype, is_numeric_type, is_scalar_type, NC
from virtmat.language.utilities.units import get_units, get_dimensionality
from virtmat.language.utilities.logging import get_logger
from virtmat.language.utilities.mongodb import get_iso_datetime
from virtmat.language.utilities.compatibility import get_grammar_version
from .instant_executor import program_value, plain_type_value


def get_input_name(par):
    """return the input name and input value of a named object"""
    inp_value = None
    if isinstance_m(par, ['ObjectImport']):
        inp_name = par.name
        inp_value = FWDataObject.from_obj(par.value)
    elif isinstance_m(par, ['Variable']):
        inp_name = par.name
    else:
        msg = 'parameter must be variable or imported object'
        get_logger(__name__).error('get_input_name: error: %s', msg)
        raise RuntimeError(msg)
    return inp_name, inp_value


def get_par_value(par):
    """Return the value property of a parameter, return NC if not available"""
    try:
        return par.value
    except NonCompletedException:
        return NC
    except TextXError as err:
        if isinstance(err.__cause__, NonCompletedException):
            return NC
        raise err


def get_fstr(func):
    """Return a pickle-serialized function as a Python3 string"""
    try:
        f_str = base64.b64encode(dill.dumps(func)).decode('utf-8')
    except dill.PicklingError:
        get_logger(__name__).error('get_fstr: pickling error')
        raise
    get_logger(__name__).debug('get_fstr: normal run')
    return f_str


def get_fws(self):
    """Create one or more Firework objects for one Variable object"""
    logger = get_logger(__name__)
    logger.debug('get_fws: processing %s', repr(self.func))
    assert isinstance(self.func, tuple) and len(self.func) == 2
    func, pars = self.func
    logger.debug('get_fws: func: %s pars: %s', self.name, pars)
    self.__fw_name = uuid.uuid4().hex
    spec_inp = {}
    spec_rsc = {}
    inputs = []
    for par in pars:
        inp_name, inp_value = get_input_name(par)
        inputs.append(inp_name)
        if inp_value is not None:
            spec_inp[inp_name] = inp_value
    spec_rsc['_source_code'] = self.source_code
    spec_rsc['_grammar_version'] = get_model(self).grammar_version
    spec_rsc['_data_schema_version'] = DATA_SCHEMA_VERSION
    if self.resources is None:
        spec_rsc['_fworker'] = get_model(self).worker_name
        spec_rsc['_category'] = 'interactive'
    else:
        spec_rsc['_fworker'] = self.resources.worker_name
        spec_rsc['_category'] = self.resources.category
        if spec_rsc['_category'] == 'batch':
            spec_rsc['_queueadapter'] = self.resources.qadapter
            spec_rsc['_queueadapter']['job_name'] = self.__fw_name
    assert spec_rsc['_category'] in ['batch', 'interactive']
    if hasattr(self, 'dupefinder'):
        spec_rsc['_dupefinder'] = self.dupefinder
    if hasattr(self, 'nchunks'):
        fws = self._get_fws_parallel(inputs, spec_rsc)
    else:
        tsk = FunctionTask(func=get_fstr(func), inputs=inputs, outputs=[self.name])
        fws = [Firework([tsk], spec={**spec_rsc, **spec_inp}, name=self.__fw_name)]
    return fws


def _get_fws_parallel(self, inputs, spec_rsc):
    """parallel Map, Filter and Reduce as parameters of Variable (self)"""
    get_logger(__name__).debug('get_fws_in_parallel: func: %s', self.name)
    if isinstance_m(self.parameter, ('Map',)):
        split = [p.ref.name for p in self.parameter.params]
    else:
        split = [self.parameter.parameter.ref.name]
    chunk_ids = [f'{self.name}_chunk_{c}' for c in range(self.nchunks)]
    tsk = ScatterTask(func=get_fstr(self.func[0]), inputs=inputs,
                      chunk_ids=chunk_ids, split=split, spec=spec_rsc)
    spec = {'_category': 'interactive', '_fworker': get_model(self).worker_name}
    spec['_source_code'] = spec_rsc['_source_code']
    spec['_grammar_version'] = get_model(self).grammar_version
    spec['_data_schema_version'] = DATA_SCHEMA_VERSION
    fw1 = Firework([tsk], spec=spec, name=uuid.uuid4().hex)
    if isinstance_m(self.parameter, ('Map', 'Filter')):
        fstr = get_fstr(lambda *x: pandas.concat(x))
        tsks = [FunctionTask(func=fstr, inputs=chunk_ids, outputs=[self.name])]
    else:
        assert isinstance_m(self.parameter, ('Reduce',))
        outp_reduce = self.name + '_for_reduce'
        fstr = get_fstr(lambda *x: x)
        tsk1 = FunctionTask(func=fstr, inputs=chunk_ids, outputs=[outp_reduce])
        inps3 = [outp_reduce if i == self.name else i for i in inputs]
        tsk2 = FunctionTask(func=get_fstr(self.func[0]), inputs=inps3,
                            outputs=[self.name])
        tsks = [tsk1, tsk2]
    fw2 = Firework(tsks, spec=spec, name=self.__fw_name)
    return [fw1, fw2]


def get_fw_object_to(self):
    """create a single Firework object for an ObjectTo object"""
    spec = {'_source_code': self.source_code, '_category': 'interactive',
            '_fworker': get_model(self).worker_name,
            '_grammar_version': get_model(self).grammar_version,
            '_data_schema_version': DATA_SCHEMA_VERSION}
    tsk = ExportDataTask(varname=self.ref.name, filename=self.filename, url=self.url)
    self.__fw_name = uuid.uuid4().hex
    return Firework([tsk], spec=spec, name=self.__fw_name)


def get_wf(self):
    """create a workflow object from a model"""
    assert self._tx_model_params['model_instance']['uuid'] is None
    fws = []
    for obj in get_children_of_type('Variable', self):
        fws.extend(obj.fireworks)
    data_nodes = [o.firework for o in get_children_of_type('ObjectTo', self)]
    outs = {}
    for fwk in fws:
        lst = []
        for task in fwk.tasks:
            if 'outputs' in task:
                lst += task['outputs']
            elif 'chunk_ids' in task:
                lst += task['chunk_ids']
        outs[str(fwk.fw_id)] = lst
    inps = {str(f.fw_id): [i for t in f.tasks for i in t['inputs']] for f in fws}
    expi = {str(f.fw_id): [t['varname'] for t in f.tasks] for f in data_nodes}
    expo = {str(f.fw_id): [] for f in data_nodes}
    inps.update(expi)
    outs.update(expo)
    fws.extend(data_nodes)
    links = {}
    # naive implementation of the join
    for ofw in fws:
        oid = ofw.fw_id
        if len(outs[str(oid)]) > 0:
            links[str(oid)] = []
            for ifw in fws:
                for inp in inps[str(ifw.fw_id)]:
                    if inp in outs[str(oid)]:
                        links[str(oid)].append(ifw.fw_id)
    # find all root nodes
    root_fws = []
    for firework in fws:
        if all('inputs' in t and len(t['inputs']) == 0 for t in firework.tasks):
            root_fws.append(firework.fw_id)

    # create a meta node for things like function definitions, imports, etc.
    meta_tasks = [FunctionTask(func=get_fstr(lambda: None), inputs=[], outputs=[])]

    meta_src = []
    for statement in ['ObjectImports', 'FunctionDefinition']:
        for obj in get_children_of_type(statement, self):
            meta_src.extend(obj.source_code)
    root_spec = {'_category': 'interactive', '_fworker': self.worker_name}
    meta_spec = {'_source_code': meta_src,
                 '_grammar_version': get_model(self).grammar_version,
                 '_data_schema_version': DATA_SCHEMA_VERSION}
    meta_spec.update(root_spec)
    tag_dct = {}
    for tag in get_children_of_type('Tag', self):
        tag_dct.update(tag_serialize(tag.value))
    meta_spec['_tag'] = tag_dct

    meta_node = Firework(meta_tasks, name='_fw_meta_node', spec=meta_spec)
    fws.append(meta_node)
    root_fws.append(meta_node.fw_id)

    # create a new empty root node
    root_node = Firework(meta_tasks, name='_fw_root_node', spec=root_spec)
    fws.append(root_node)

    # link all root nodes to the new root node
    links[str(root_node.fw_id)] = root_fws

    grammar_str = self._tx_model_params.get('grammar_str')
    metadata = {'uuid': self.uuid, 'g_uuid': self.g_uuid, 'grammar_str': grammar_str,
                'data_schema_version': DATA_SCHEMA_VERSION}
    name = 'Created by textS/textM interpreter'
    return Workflow(fws, links_dict=links, metadata=metadata, name=name)


@textxerror_wrap
@checktype
@settype
def variable_value(self):
    """obtain an output value from database: asynchronously and non-blocking"""
    logger = get_logger(__name__)
    logger.debug('variable_value:%s', repr(self))
    model = get_model(self)
    fw_p = {'state': True, 'fw_id': True, 'launches': True}
    fw_dct = model.lpad.fireworks.find_one({'name': self.__fw_name}, fw_p)
    if fw_dct['state'] == 'COMPLETED':
        return retrieve_value(model.lpad, fw_dct['launches'][-1], self.name)
    if fw_dct['state'] == 'FIZZLED':
        launch_q = {'launch_id': fw_dct['launches'][-1]}
        launch_dct = model.lpad.launches.find_one(launch_q, {'action': True})
        if '_exception' in launch_dct['action']['stored_data']:
            logger.error('variable_value:%s evaluation error', repr(self))
            exception_dct = launch_dct['action']['stored_data']['_exception']
            trace = exception_dct['_stacktrace']
            if exception_dct.get('_details') is None:
                raise EvaluationError(f'No details found. Stacktrace:\n{trace}')
            pkl = exception_dct['_details']['pkl']
            exc = dill.loads(base64.b64decode(pkl.encode()))
            if isinstance(exc, TEXTX_WRAPPED_EXCEPTIONS):
                raise exc
            lst = traceback.format_exception(type(exc), exc, exc.__traceback__)
            raise EvaluationError(''.join(lst)) from exc
        raise EvaluationError('state FIZZLED but no exception found')
    if fw_dct['state'] == 'WAITING':
        parents = get_ancestors(model.lpad, fw_dct['fw_id'])
        fw_q = {'fw_id': {'$in': parents}, 'state': 'FIZZLED'}
        fizzled = list(model.lpad.fireworks.find(fw_q, projection={'name': True}))
        if fizzled:
            msg = f'Evaluation of {self.name} not possible due to failed ancestors: '
            var_names = []
            vars_ = get_children_of_type('Variable', model)
            for fwk in fizzled:
                try:
                    var_name = next(v.name for v in vars_ if v.__fw_name == fwk['name'])
                except StopIteration:
                    var_name = fwk['name']
                var_names.append(var_name)
            msg += ', '.join(var_names)
            logger.error('variable_value:%s ancestor error', repr(self))
            raise AncestorEvaluationError(msg)
        raise NonCompletedException
    if fw_dct['state'] in ['READY', 'RESERVED', 'RUNNING']:
        raise NonCompletedException
    logger.critical('variable_value:%s unknown node state', repr(self))
    raise RuntimeError('Unknown node state')


@error_handler
def print_value(self):
    """evaluate the print function"""
    values = []
    for par in self.params:
        try:
            val = par.value
        except TextXError as err:
            if isinstance(err.__cause__, NonCompletedException):
                val = NC
            else:
                raise err
        values.append(formatter(val))
    return ' '.join(values)


def type_value(self):
    """evaluate the type function object"""
    parval = get_par_value(self.param)
    name = self.param.ref.name if isinstance_m(self.param, ['GeneralReference']) else None
    datatype = getattr(getattr(self.param.type_, 'datatype', None), '__name__', None)
    dct = {'name': name,
           'type': self.param.type_.__name__,
           'scalar': is_scalar_type(self.param.type_),
           'numeric': is_numeric_type(self.param.type_),
           'datatype': datatype}
    if is_numeric_type(self.param.type_) and parval is not NC:
        dct['dimensionality'] = str(get_dimensionality(parval))
        dct['units'] = str(get_units(parval))
    if isinstance_m(self.param, ['GeneralReference']):
        model = get_model(self)
        var_list = get_children_of_type('Variable', model)
        var = next(v for v in var_list if v.name == self.param.ref.name)
        fw_q = {'name': var.__fw_name}
        wf_q = {'metadata.uuid': model.uuid}
        fw_proj = {'fw_id': True, 'name': True, 'state': True,
                   'created_on': True, 'updated_on': True, 'launches': True}
        wf_proj = {'metadata.g_uuid': True, 'parent_links': True}
        wfs = get_nodes_info(model.lpad, wf_q, fw_q, fw_proj, wf_proj)
        assert len(wfs) == 1
        assert len(wfs[0]['nodes']) == 1
        node = wfs[0]['nodes'][0]
        dct.update({
           'node ID': node['fw_id'],
           'node UUID': var.__fw_name,
           'node state': node['state'],
           'number of launches': len(node['launches']),
           'created on': get_iso_datetime(node['created_on']),
           'updated on': get_iso_datetime(node['updated_on']),
           'parent IDs': wfs[0]['parent_links'].get(str(node['fw_id']), []),
           'model UUID': model.uuid,
           'group UUID': wfs[0]['metadata']['g_uuid']})
    return pandas.DataFrame([dct])


@textxerror_wrap
@checktype
def func_value(self):
    """evaluate a python function object"""
    get_logger(__name__).debug('func_value:%s', repr(self))
    func, pars = self.func
    assert all(isinstance_m(p, ['Variable', 'ObjectImport']) for p in pars)
    return func(*[p.value for p in pars])


def get_lpad(self):
    """return launchpad object associated with the model"""
    return self._tx_model_params['model_instance']['lpad']


def get_uuid(self):
    """return workflow uuid associated with the model"""
    input_uuid = self._tx_model_params['model_instance']['uuid']
    return uuid.uuid4().hex if input_uuid is None else input_uuid


def get_g_uuid(self):
    """return group uuid of the model"""
    muuid = self._tx_model_params['model_instance']['uuid']
    g_uuid = self._tx_model_params['model_instance'].get('g_uuid')
    if muuid is not None:
        wf_q = {'metadata.uuid': self.uuid}
        wfl = self.lpad.workflows.find_one(wf_q, projection={'metadata': True})
        assert wfl is not None
        assert wfl['metadata'].get('g_uuid') == g_uuid
        return g_uuid
    if g_uuid is None:
        return uuid.uuid4().hex
    return g_uuid


def get_fw_ids_torun(self):
    """return the list of nodes for which evaluation has been requested"""
    vars_ = set()
    for prnt in get_children_of_type('Print', self):
        vrefs = get_children_of_type('GeneralReference', prnt)
        vars_.update(vref.ref for vref in vrefs)
    fw_ids = []
    for var in iter(vars_):
        fw_ids.extend(self.lpad.get_fw_ids({'name': var.__fw_name}))
    anc_ids = [a for i in fw_ids for a in get_ancestors(self.lpad, i)]
    return list(set(fw_ids+anc_ids))


def get_list_of_names(self):
    """return a list of the names of all named objects"""
    classes = ['Variable', 'FunctionDefinition', 'ObjectImport']
    objects = get_children(lambda x: isinstance_m(x, classes), self)
    return [obj.name for obj in objects]


def get_my_grammar_version(self):
    """get grammar version from grammar string"""
    if self._tx_model_params.get('grammar_str') is not None:
        return get_grammar_version(self._tx_model_params.get('grammar_str'))
    return None


def add_workflow_properties(metamodel):
    """Add class properties using monkey style patching"""

    metamodel['Program'].value = property(program_value)
    metamodel['Program'].fw_ids_torun = property(get_fw_ids_torun)
    metamodel['Program'].lpad = property(get_lpad)
    metamodel['Program'].uuid = cached_property(get_uuid)
    metamodel['Program'].uuid.__set_name__(metamodel['Program'], 'uuid')
    metamodel['Program'].g_uuid = cached_property(get_g_uuid)
    metamodel['Program'].g_uuid.__set_name__(metamodel['Program'], 'g_uuid')
    metamodel['Program'].workflow = cached_property(get_wf)
    metamodel['Program'].workflow.__set_name__(metamodel['Program'], 'workflow')
    metamodel['Program'].name_list = cached_property(get_list_of_names)
    metamodel['Program'].name_list.__set_name__(metamodel['Program'], 'name_list')
    metamodel['Program'].grammar_version = cached_property(get_my_grammar_version)
    metamodel['Program'].grammar_version.__set_name__(metamodel['Program'], 'grammar_version')

    metamodel['Print'].value = property(print_value)
    metamodel['Type'].value = property(type_value)

    metamodel['Variable'].fireworks = cached_property(get_fws)
    metamodel['Variable'].fireworks.__set_name__(metamodel['Variable'], 'firework')
    metamodel['Variable']._get_fws_parallel = _get_fws_parallel
    metamodel['ObjectTo'].firework = cached_property(get_fw_object_to)
    metamodel['ObjectTo'].firework.__set_name__(metamodel['ObjectTo'], 'firework')

    mapping_dict = {
        'Variable': variable_value,
        'Tag': func_value,
        'Dict': func_value,
        'GeneralReference': func_value,
        'FunctionCall': func_value,
        'IfFunction': func_value,
        'IfExpression': func_value,
        'Expression': func_value,
        'Or': func_value,
        'Comparison': func_value,
        'Series': func_value,
        'Table': func_value,
        'IterableProperty': func_value,
        'IterableQuery': func_value,
        'ObjectImport': func_value,
        'Quantity': func_value,
        'String': textxerror_wrap(plain_type_value),
        'Bool': textxerror_wrap(plain_type_value),
        'PrintParameter': func_value,
        'BoolArray': func_value,
        'StrArray': func_value,
        'IntArray': func_value,
        'FloatArray': func_value,
        'ComplexArray': func_value,
        'IntSubArray': func_value,
        'FloatSubArray': func_value,
        'ComplexSubArray': func_value
    }
    for key, func in mapping_dict.items():
        metamodel[key].value = cached_property(func)
        metamodel[key].value.__set_name__(metamodel[key], 'value')


def append_var_nodes(model):
    """append Variable nodes to workflow after resolving their dependencies"""
    logger = get_logger(__name__)
    nodes = []
    for var in get_children_of_type('Variable', model):
        fw_ids = get_nodes_providing(model.lpad, model.uuid, var.name)
        if len(fw_ids) != 0:
            assert len(fw_ids) == 1
            if getattr(var, '_update', None):
                logger.debug(' updating variable: %s', var.name)
                assert len(var.fireworks) == 1
                fwk = var.fireworks[0].to_dict()
                logger.debug(' updating spec: %s', fwk['spec'])
                safe_update(model.lpad, fw_ids[0], fwk['spec'])
            fwk = model.lpad.fireworks.find_one({'fw_id': fw_ids[0]}, {'name': True})
            var.__fw_name = fwk['name']
        else:
            nodes.extend(var.fireworks)
    nodes_len = len(nodes)
    logger.debug('appending %s new variable nodes', nodes_len)
    while nodes:
        num_nodes = len(nodes)
        for ind, node in enumerate(nodes):
            get_logger(__name__).debug('trying to append %s', node)
            parents = get_parent_nodes(model.lpad, model.uuid, node)
            if None not in parents:
                get_logger(__name__).debug('appending %s, parents %s', node, parents)
                model.lpad.append_wf(Workflow([nodes.pop(ind)]), fw_ids=parents)
                break
        assert len(nodes) < num_nodes
    logger.debug('appended %s new variable nodes', nodes_len)


def append_output_nodes(model):
    """check ObjectTo objects and append ObjectTo nodes to workflow"""
    logger = get_logger(__name__)
    for obj_to in get_children_of_type('ObjectTo', model):
        wf_query = {'metadata.uuid': model.uuid}
        fw_query = {'spec._tasks.0.varname': obj_to.ref.name,
                    'spec._tasks.0.filename': obj_to.filename,
                    'spec._tasks.0.url': obj_to.url}
        fw_proj = {'name': True}
        wfs = get_nodes_info(model.lpad, wf_query, fw_query, fw_proj)
        nodes = next(wf['nodes'] for wf in wfs)
        if nodes:
            assert len(nodes) == 1
            obj_to.__fw_name = next(n['name'] for n in nodes)
        else:
            parents = get_nodes_providing(model.lpad, model.uuid, obj_to.ref.name)
            model.lpad.append_wf(Workflow([obj_to.firework]), fw_ids=parents)
            logger.debug('added output node for var %s', obj_to.ref.name)


def update_meta_node(model):
    """update the meta node with tags, object imports and function definitions"""
    meta_src = []
    for statement in ['ObjectImports', 'FunctionDefinition']:
        for obj in get_children_of_type(statement, model):
            meta_src.extend(obj.source_code)
    wf_q = {'metadata.uuid': model.uuid}
    fw_q = {'name': '_fw_meta_node'}
    fw_p = {'spec': True, 'fw_id': True}
    wfs = get_nodes_info(model.lpad, wf_q, fw_q, fw_p)
    assert len(wfs) == 1
    assert len(wfs[0]['nodes']) == 1
    fwk = wfs[0]['nodes'][0]
    if sorted(fwk['spec']['_source_code']) != sorted(meta_src):
        safe_update(model.lpad, fwk['fw_id'], {'_source_code': meta_src})
        get_logger(__name__).info('updated meta node %s: _source_code: %s',
                                  fwk['fw_id'], meta_src)
    tags = get_children_of_type('Tag', model)
    if tags:
        tag_dct = fwk['spec'].get('_tag') or {}
        for tag in tags:
            tag_dct.update(tag_serialize(tag.value))
        safe_update(model.lpad, fwk['fw_id'], {'_tag': tag_dct})
        get_logger(__name__).info('updated meta node %s: _tag: %s', fwk['fw_id'],
                                  formatter(tag_dct))


def workflow_model_processor(model, _):
    """generate a workflow for the just created model"""
    logger = get_logger(__name__)
    if not isinstance(model, str):
        model_params = getattr(model, '_tx_model_params')
        if model_params['model_instance']['uuid'] is None:
            logger.info('creating model from scratch')
            model.lpad.add_wf(model.workflow)
            logger.info('created model with UUID %s', model.uuid)
        else:
            logger.info('extending model with UUID %s', model.uuid)
            append_var_nodes(model)
            append_output_nodes(model)
            update_meta_node(model)
            logger.info('extended model with UUID %s', model.uuid)
        if model_params.get('autorun'):
            logger.info('running model with UUID %s', model.uuid)

            def get_fws_torun():
                """return a list of fireworks if there are READY fireworks"""
                fw_q = {'state': 'READY', 'spec._category': 'interactive'}
                if model_params.get('on_demand'):
                    fw_q.update({'fw_id': {'$in': model.fw_ids_torun}})
                    return model.lpad.get_fw_ids(fw_q)
                wf_q = {'metadata.uuid': model.uuid}
                return model.lpad.get_fw_ids_in_wfs(wf_q, fw_q)

            unique_launchdir = model_params.get('unique_launchdir', False)
            fws_to_run = get_fws_torun()
            while fws_to_run:
                run_fireworks(model.lpad, fws_to_run, worker_name=model.worker_name,
                              create_subdirs=unique_launchdir)
                fws_to_run = get_fws_torun()
    else:
        logger.info('empty model')
