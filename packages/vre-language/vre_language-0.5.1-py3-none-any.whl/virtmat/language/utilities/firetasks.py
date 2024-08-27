"""custom firetasks for use in the interpreter"""
import base64
import dill
import pandas
import numpy
from fireworks import Firework
from fireworks.core.firework import FWAction, FireTaskBase
from virtmat.language.utilities.serializable import FWDataObject
from virtmat.language.utilities.ioops import store_value


class FunctionTask(FireTaskBase):
    """call a pickled function with JSON serializable inputs, return JSON
    serializable outputs"""
    _fw_name = '{{' + __loader__.name + '.' + __qualname__ + '}}'
    required_params = ['func', 'inputs', 'outputs']

    def run_task(self, fw_spec):
        inputs = self.get('inputs', [])
        assert isinstance(inputs, list)
        try:
            params = [fw_spec[i].value for i in inputs]
            func = dill.loads(base64.b64decode(self['func'].encode()))
            f_output = func(*params)
        except BaseException as err:
            # serialize and raise the exception
            # https://materialsproject.github.io/fireworks/failures_tutorial.html
            cls = err.__class__
            dct = {'name': cls.__name__, 'module': cls.__module__, 'msg': str(err),
                   'pkl': base64.b64encode(dill.dumps(err)).decode('utf-8')}
            err.to_dict = lambda: dct
            raise err
        return self.get_fw_action(f_output)

    def get_fw_action(self, output):
        """construct a FWAction object from the output of a function"""
        outputs = self.get('outputs', [])
        assert isinstance(outputs, list)
        assert all(isinstance(o, str) for o in outputs)
        actions = {}
        if len(outputs) == 1:
            actions['update_spec'] = {outputs[0]: FWDataObject.from_obj(output)}
        elif len(outputs) > 1:
            assert isinstance(output, (list, tuple, set))
            assert len(output) == len(outputs)
            output_data = (FWDataObject.from_obj(o) for o in output)
            actions['update_spec'] = dict(zip(outputs, output_data))
        return FWAction(**actions)


class ExportDataTask(FireTaskBase):
    """export specified data to a file or url"""
    _fw_name = '{{' + __loader__.name + '.' + __qualname__ + '}}'
    required_params = ['varname']
    optional_params = ['filename', 'url']

    def run_task(self, fw_spec):
        obj_val = fw_spec[self.get('varname')].value
        store_value(obj_val, self.get('url'), self.get('filename'))
        return FWAction()


class ScatterTask(FireTaskBase):
    """implement parallelized map function as a dynamic sub-workflow"""
    _fw_name = '{{' + __loader__.name + '.' + __qualname__ + '}}'
    required_params = ['func', 'split', 'inputs', 'chunk_ids', 'spec']

    def run_task(self, fw_spec):
        assert isinstance(self['inputs'], list)
        assert isinstance(self['chunk_ids'], list)
        assert isinstance(self['split'], list)
        assert all(isinstance(i, str) for i in self['inputs'])
        assert all(isinstance(o, str) for o in self['chunk_ids'])
        assert all(isinstance(i, str) for i in self['split'])
        assert len(set((len(fw_spec[i].value) for i in self['split']))) == 1
        nchunks = len(self['chunk_ids'])

        dcts = [self['spec'].copy() for _ in range(nchunks)]
        for inp in self['split']:
            assert isinstance(fw_spec[inp].value, (pandas.Series, pandas.DataFrame))
            chunks = numpy.array_split(fw_spec[inp].value, nchunks)
            for dct, chunk in zip(dcts, chunks):
                dct[inp] = FWDataObject.from_obj(chunk)
        for inp in self['inputs']:
            if inp not in self['split']:
                for dct in dcts:
                    dct[inp] = fw_spec[inp]
        fireworks = []
        for chunk_id, dct in zip(self['chunk_ids'], dcts):
            task = FunctionTask(func=self['func'], inputs=self['inputs'],
                                outputs=[chunk_id])
            fireworks.append(Firework(task, spec=dct, name=chunk_id))
        return FWAction(detours=fireworks)
