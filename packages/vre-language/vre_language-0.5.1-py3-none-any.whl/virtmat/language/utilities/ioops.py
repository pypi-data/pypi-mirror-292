""" i/o operations """
import os
import pathlib
import uuid
import json
import zlib
from urllib.request import urlopen
# from urllib import request, parse
import yaml
from gridfs import GridFS
from fireworks import LaunchPad
from fireworks.fw_config import LAUNCHPAD_LOC
from fireworks.utilities.fw_serializers import load_object, recursive_dict
from virtmat.language.utilities.errors import RuntimeTypeError, RuntimeValueError
from virtmat.language.utilities.amml import AMMLStructure


def load_value(url=None, filename=None):
    """load data from file or from URL using the GET method"""
    assert url or filename, 'either filename or url must be specified'
    if filename:
        with open(filename, 'r', encoding='utf-8') as inp:
            val = yaml.safe_load(inp)
    elif url:
        with urlopen(url) as inp:
            val = yaml.safe_load(inp)
    if isinstance(val, dict):
        val = load_object(val)
    return val


def store_value(val, url=None, filename=None):
    """store serializable data to a new file or to an URL using the POST method"""
    assert url or filename, 'either filename or url must be specified'
    if filename:
        if pathlib.Path(filename).suffix in ('.yml', '.yaml'):
            with open(filename, 'x', encoding='utf-8') as out:
                yaml.safe_dump(recursive_dict(val), out)
        elif isinstance(val, AMMLStructure):
            val.to_ase_file(filename)
        else:
            msg = f'unknown format {filename} or data type {type(val)}'
            raise RuntimeTypeError(msg)
    elif url:
        raise NotImplementedError
        # data = parse.urlencode(val).encode()
        # req =  request.Request(url, data=data)
        # resp = request.urlopen(req)


def get_datastore_config(**kwargs):
    """update, set globally and return the data store configuration"""
    fw_config = os.path.join(os.path.expanduser('~'), '.fireworks')
    config = {'path': os.path.join(fw_config, 'vre-language-datastore'),
              'type': 'gridfs',  # in ['file', 'gridfs', 'url', None]
              'format': 'json',  # in ['json', 'yaml', 'hdf5']
              'name': 'vre_language_datastore',
              'launchpad': LAUNCHPAD_LOC,
              'compress': True,
              'inline-threshold': 1000000}
    if 'DATASTORE_CONFIG' in os.environ:
        conf_path = os.environ['DATASTORE_CONFIG']
    else:
        conf_path = os.path.join(fw_config, 'datastore_config.yaml')
    if os.path.exists(conf_path):
        with open(conf_path, 'r', encoding='utf-8') as inp:
            custom_config = yaml.safe_load(inp)
        config.update(custom_config)
    if config['type'] == 'file' and not os.path.exists(config['path']):
        os.makedirs(config['path'], exist_ok=True)
    config.update(kwargs)
    globals()['DATASTORE_CONFIG'] = config
    return config


class GridFSDataStore(list):
    """store a list of unique GridFS datastores"""

    def add(self, conf, lpad=None):
        """add a datastore with a configuration and launchpad object lpad"""
        if conf['type'] != 'gridfs':
            return
        if self._get(conf) is None:
            lp_f = conf.get('launchpad')
            config = {'launchpad': lp_f, 'name': conf['name']}
            if lpad is None:
                lpad = LaunchPad() if lp_f is None else LaunchPad.from_file(lp_f)
            config['gridfs'] = GridFS(lpad.db, conf['name'])
            self.append(config)

    def get(self, conf):
        """get a datastore and add it if not yet included"""
        if conf['type'] == 'gridfs' and self._get(conf) is None:
            self.add(conf)
        return self._get(conf)

    def _get(self, conf):
        """get a datastore for specified configuration conf"""
        for entry in self:
            if (entry['launchpad'] == conf.get('launchpad')
               and entry['name'] == conf['name']):
                return entry['gridfs']
        return None


def offload_data(data):
    """offload json serializable data to a store"""
    datastore = DATASTORE_CONFIG
    if datastore['type'] is None:
        return datastore, None
    if datastore['format'] != 'json':
        msg = f"datastore format {datastore['format']} not implemented"
        raise NotImplementedError(msg)
    filename = uuid.uuid4().hex + '.json'
    if datastore['compress']:
        filename += '.zz'
    if datastore['type'] == 'file':
        if datastore['compress']:
            path = os.path.join(datastore['path'], filename)
            with open(path, 'xb') as out:
                out.write(zlib.compress(json.dumps(data).encode()))
        else:
            path = os.path.join(datastore['path'], filename)
            with open(path, 'x', encoding='utf-8') as out:
                json.dump(data, out)
    elif datastore['type'] == 'gridfs':
        bytes_ = json.dumps(data).encode()
        bytes_ = zlib.compress(bytes_) if datastore['compress'] else bytes_
        GRIDFS_DATASTORE.get(datastore).put(bytes_, filename=filename)
    else:
        msg = f"datastore type {datastore['type']} not implemented"
        raise NotImplementedError(msg)
    return datastore, filename


def lade_data(datastore, filename):
    """get json serializable data from a store"""
    if datastore['type'] is None:
        raise RuntimeValueError(f"invalid datastore type {datastore['type']}")
    if datastore['type'] == 'file':
        path = os.path.join(datastore['path'], filename)
        if datastore['compress']:
            with open(path, 'rb') as inp:
                val = json.loads(zlib.decompress(inp.read()).decode())
        else:
            with open(path, 'r', encoding='utf-8') as inp:
                val = json.load(inp)
    elif datastore['type'] == 'gridfs':
        with GRIDFS_DATASTORE.get(datastore).find_one({'filename': filename}) as inp:
            if datastore['compress']:
                val = json.loads(zlib.decompress(inp.read()).decode())
            else:
                val = json.load(inp)
    else:
        msg = f"datastore type {datastore['type']} not implemented"
        raise NotImplementedError(msg)
    return val


GRIDFS_DATASTORE = GridFSDataStore()
DATASTORE_CONFIG = get_datastore_config()
