"""manage sessions for dynamic model processing / incremental development"""
import os
from functools import cached_property
from textx import metamodel_from_file, textx_isinstance
from virtmat.language.metamodel.processors import table_processor, null_processor, number_processor
from virtmat.language.utilities.textx import GRAMMAR_LOC
from virtmat.language.utilities.errors import error_handler, ModelNotFoundError
from virtmat.language.utilities.errors import textxerror_wrap, UpdateError, QueryError
from virtmat.language.utilities.logging import get_logger
from virtmat.language.utilities.formatters import formatter
from virtmat.language.utilities.fireworks import get_nodes_providing
from virtmat.language.utilities.serializable import tag_serialize
from virtmat.language.utilities.types import checktype
from virtmat.language.utilities.mongodb import get_iso_datetime
from virtmat.language.constraints.typechecks import (tuple_type, series_type, table_type,
                                                     dict_type, array_type, quantity_type)
from .instant_executor import (tuple_value, series_value, table_value, dict_value,
                               bool_str_array_value, numeric_array_value,
                               numeric_subarray_value, plain_type_value, quantity_value)
from .session import Session


def add_value_session_model(metamodel):
    """add the value-property for objects of session manager models"""
    mapping_dict = {
        'Tuple': tuple_value,
        'Series': series_value,
        'Table': table_value,
        'Dict': dict_value,
        'BoolArray': bool_str_array_value,
        'StrArray': bool_str_array_value,
        'IntArray': numeric_array_value,
        'FloatArray': numeric_array_value,
        'ComplexArray': numeric_array_value,
        'IntSubArray': numeric_subarray_value,
        'FloatSubArray': numeric_subarray_value,
        'ComplexSubArray': numeric_subarray_value,
        'String': plain_type_value,
        'Bool': plain_type_value,
        'Quantity': quantity_value
    }
    for key, func in mapping_dict.items():
        metamodel[key].value = cached_property(textxerror_wrap(checktype(func)))
        metamodel[key].value.__set_name__(metamodel[key], 'value')
    metamodel['Null'].value = None


def add_types_session_model(metamodel):
    """add the type-property for objects of session manager models"""
    mapping_dict = {
        'Tuple': tuple_type,
        'Series': series_type,
        'Table': table_type,
        'Dict': dict_type,
        'BoolArray': array_type,
        'StrArray': array_type,
        'IntArray': array_type,
        'FloatArray': array_type,
        'ComplexArray': array_type,
        'IntSubArray': array_type,
        'FloatSubArray': array_type,
        'ComplexSubArray': array_type,
        'Quantity': quantity_type
    }
    for key, function in mapping_dict.items():
        metamodel[key].type_ = cached_property(textxerror_wrap(function))
        metamodel[key].type_.__set_name__(metamodel[key], 'type_')
    metamodel['Bool'].type_ = bool
    metamodel['String'].type_ = str


def expand_query_prefix(query):
    """expand the path prefix in query keys"""
    p_map = {'tags': 'spec._tag.', 'meta': '', 'data': 'spec.'}
    if not all(k in ('tags', 'meta', 'data') for k in query.keys()):
        raise QueryError('query must include tags, meta or data keys')

    def _recursive_q(obj, prefix):
        if isinstance(obj, dict):
            out = {}
            for key, val in obj.items():
                key = prefix + key[1:] if key[0] == '~' else key
                out[key] = _recursive_q(val, prefix)
            return out
        if isinstance(obj, (tuple, list)):
            return [_recursive_q(e, prefix) for e in obj]
        return obj

    return {k: _recursive_q(v, p_map[k]) for k, v in query.items()}


class SessionManager():
    """session manager for basic interactive work using a text terminal"""

    def __init__(self, lpad, **kwargs):
        self.lpad = lpad
        self.kwargs = dict(kwargs)
        del self.kwargs['uuid']
        del self.kwargs['grammar_path']
        del self.kwargs['model_path']
        create_new = not bool(kwargs['model_path'])
        self.session = Session(lpad, create_new=create_new, **kwargs)
        self.uuid = self.session.uuids[0]
        self.grammar_path = kwargs['grammar_path'] or GRAMMAR_LOC
        session_grammar = os.path.join(os.path.dirname(GRAMMAR_LOC), 'session.tx')
        self.metamodel = metamodel_from_file(session_grammar, auto_init_attributes=False)
        add_types_session_model(self.metamodel)
        add_value_session_model(self.metamodel)
        obj_processors = {'Null': null_processor, 'Number': number_processor,
                          'Table': table_processor}
        self.metamodel.register_obj_processors(obj_processors)

    @error_handler
    def get_model_value(self, *args, **kwargs):
        """wrapped and evaluated version of get_model() of the Session class"""
        return getattr(self.session.get_model(*args, uuid=self.uuid, **kwargs), 'value', '')

    def main_loop(self):
        """this is the main loop of the interactive session"""
        while True:
            try:
                input_str = input('Input > ')
            except EOFError:
                print('\nExiting')
                self.session.stop_runner()
                break
            except KeyboardInterrupt:
                print('\nType %exit or %close or Ctrl+D to close session')
                continue
            if not input_str.strip():
                continue
            if self.process_input(input_str):
                break

    @error_handler
    def process_input(self, input_str):
        """create a session model from input string"""
        model = self.metamodel.model_from_str(input_str)
        get_logger(__name__).debug('process_input: session model: %s', model)
        if textx_isinstance(model, self.metamodel['Magic']):
            if model.com in ('exit', 'bye', 'close', 'quit'):
                print('Exiting')
                self.session.stop_runner()
                return True
            self.process_magic(model)
            return False
        if textx_isinstance(model, self.metamodel['Expression']):
            output = self.get_model_value(model_str=f'print({input_str})')
            if output is not None:
                print('Output >', output)
            return False
        assert textx_isinstance(model, self.metamodel['Program'])
        output = self.get_model_value(model_str=input_str)
        if output:
            print('Output >', output)
        return False

    @error_handler
    def process_magic(self, model):
        """process a magic command model"""
        if model.com == 'stop':
            self.session.stop_runner()
        elif model.com == 'start':
            self.session.start_runner()
        elif model.com == 'sleep':
            if self.session.wfe:
                if model.arg is None:
                    print(self.session.wfe.sleep_time)
                else:
                    self.session.wfe.sleep_time = model.arg
        elif model.com == 'new':
            start_thread = self.is_launcher_running()
            if start_thread:
                self.session.stop_runner()
            self.session = Session(self.lpad, create_new=True,
                                   grammar_path=self.grammar_path, **self.kwargs)
            self.uuid = self.session.uuids[0]
            if start_thread:
                self.session.start_runner()
            print(f'Started new session with uuids {formatter(self.session.uuids)}')
        elif model.com == 'uuid':
            if model.arg is None:
                print('uuids:', formatter(self.uuid), formatter(self.session.uuids))
            elif model.arg != self.uuid:
                self.switch_model(model.arg)
        elif model.com == 'vary':
            print('vary:', formatter(self.session.get_vary_df()))
        elif model.com in ('hist', 'history'):
            print(self.session.get_model_history(self.uuid))
        elif model.com == 'tag':
            print(formatter(self.session.get_model_tag()))
        elif model.com == 'find':
            get_logger(__name__).debug('process_magic: find: %s', formatter(model.arg.value))
            q_dict = expand_query_prefix(tag_serialize(model.arg.value))
            get_logger(__name__).debug('process_magic: query: %s', (q_dict))
            q_data = q_dict.get('data')
            q_tags = q_dict.get('tags')
            fw_q = q_tags and {'name': '_fw_meta_node', **q_tags}
            wf_ids = self.lpad.get_fw_ids_in_wfs(q_dict.get('meta'), fw_query=fw_q)
            if q_data:
                wf_q = {'nodes': {'$in': wf_ids}}
                wf_ids = self.lpad.get_fw_ids_in_wfs(wf_q, q_data)
            wf_p = {'metadata.uuid': True, 'state': True, 'updated_on': True}
            wfs = list(self.lpad.workflows.find({'nodes': {'$in': wf_ids}}, wf_p))
            if model.load_one:
                wf_uuids = [wf['metadata']['uuid'] for wf in wfs]
                if self.uuid not in wf_uuids:
                    self.switch_model(wf_uuids[0])
                print('uuids:', formatter(self.uuid), formatter(self.session.uuids))
            else:
                lines = []
                for wf in wfs:
                    lines.append(' '.join((f'{wf["state"]:10}',
                                 get_iso_datetime(wf['updated_on']),
                                 wf['metadata']['uuid'])))
                print('\n'.join(lines))
        else:
            assert model.com == 'rerun'
            for name in model.args:
                fw_ids = get_nodes_providing(self.lpad, self.uuid, name)
                if len(fw_ids) == 0:
                    raise UpdateError(f'Variable {name} not found in the model.')
                assert len(fw_ids) == 1
                self.lpad.rerun_fw(fw_ids[0])

    def is_launcher_running(self):
        """return True if launcher thread has been started and is running"""
        return (self.session.wfe and self.session.wfe.thread and
                self.session.wfe.thread.is_alive())

    def switch_model(self, new_uuid):
        """switch from one to another model"""
        if new_uuid in self.session.uuids:
            self.uuid = new_uuid
        else:
            start_thread = self.is_launcher_running()
            if start_thread:
                self.session.stop_runner()
            try:
                self.session = Session(self.lpad, uuid=new_uuid, **self.kwargs)
            except ModelNotFoundError as err:
                if start_thread:
                    self.session.start_runner()
                raise err
            self.uuid = new_uuid
            if start_thread:
                self.session.start_runner()
