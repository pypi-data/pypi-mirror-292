"""helper functions to interface fireworks"""
import os
from fireworks import Workflow, FWorker
from fireworks.utilities.fw_serializers import load_object
from fireworks.core.rocket_launcher import rapidfire, launch_rocket
from virtmat.language.utilities.errors import FILE_READ_EXCEPTIONS, ObjectFromFileError


def run_fireworks(lpad, fw_ids, worker_name=None, create_subdirs=False):
    """launch fireworks with the provided fw_ids"""
    worker = FWorker(name=worker_name, query={'fw_id': {'$in': fw_ids}})
    if create_subdirs:
        rapidfire(lpad, fworker=worker, nlaunches=0, strm_lvl=lpad.strm_lvl)
    for _ in fw_ids:
        launch_rocket(lpad, fworker=worker, strm_lvl=lpad.strm_lvl)


def get_nodes_providing(lpad, uuid, name):
    """find all nodes providing an output name in a workflow with given uuid"""
    return lpad.get_fw_ids_in_wfs({'metadata.uuid': uuid}, {'spec._tasks.outputs': name})


def get_root_node_ids(lpad, uuid):
    """find the special root node in a workflow with given uuid"""
    return lpad.get_fw_ids_in_wfs({'metadata.uuid': uuid}, {'name': '_fw_root_node'})


def get_parent_nodes(lpad, uuid, firework):
    """find parent nodes for a new firework in a workflow with a given uuid"""
    if all('inputs' in t and len(t['inputs']) == 0 for t in firework.tasks):
        parents = get_root_node_ids(lpad, uuid)
        assert len(parents) == 1
    else:
        inputs = [i for t in firework.tasks for i in t['inputs']]
        parents = set()
        for inp in inputs:
            nodes = get_nodes_providing(lpad, uuid, inp)
            if len(nodes) != 0:
                assert len(nodes) == 1
                parents.update(nodes)
            elif inp in firework.spec:
                parents.add('root_node')
            else:
                parents.add(None)
        assert len(parents) > 0
        if 'root_node' in parents:
            parents.remove('root_node')
            if len(parents) == 0:
                parents = get_root_node_ids(lpad, uuid)
                assert len(parents) == 1
    return list(parents)


def get_ancestors(lpad, fw_id):
    """return a list of all ancestors' fw_ids of a node with fw_id"""
    wfl = get_nodes_info(lpad, {'nodes': fw_id}, {}, {'_id': True}, {'links': True})
    wfl_pl = Workflow.Links.from_dict(wfl[0]['links']).parent_links
    parents = wfl_pl.get(fw_id, [])
    ancestors = set()
    while parents:
        ancestors.update(parents)
        new_parents = set()
        for par in iter(parents):
            new_parents.update(wfl_pl.get(par, []))
        parents = new_parents
    return list(ancestors)


def safe_update(lpad, fw_id, update_dict):
    """update the node spec in a safe way"""
    state = lpad.fireworks.find_one({'fw_id': fw_id}, {'state': True})['state']
    if state == 'COMPLETED':
        lpad.defuse_fw(fw_id)
        lpad.update_spec([fw_id], update_dict)
        lpad.reignite_fw(fw_id)
    elif state in ['WAITING', 'READY']:
        lpad.update_spec([fw_id], update_dict)
    elif state == 'FIZZLED':
        lpad.update_spec([fw_id], update_dict)
        lpad.rerun_fw(fw_id)


def get_nodes_info_mongodb(lpad, wf_query, fw_query, fw_proj, wf_proj=None):
    """find all nodes for each matching workflow and returns selected info"""
    wfp = {'metadata.uuid': True} if wf_proj is None else dict(wf_proj)
    fw_pipeline = [{'$match': {**fw_query, '$expr': {'$in': ['$fw_id', '$$mynodes']}}},
                   {'$project': {**fw_proj, '_id': False}}]
    wf_lookup = {'from': 'fireworks', 'let': {'mynodes': '$nodes'},
                 'pipeline': fw_pipeline, 'as': 'nodes'}
    wf_pipeline = [{'$match': wf_query}, {'$lookup': wf_lookup},
                   {'$project': {'_id': False, 'nodes': True, **wfp}}]
    cursor = lpad.workflows.aggregate(wf_pipeline)
    return list(cursor)


def get_nodes_info_mongomock(lpad, wf_query, fw_query, fw_proj, wf_proj=None):
    """find all nodes for each matching workflow and returns selected info"""
    wfp = {'metadata.uuid': True} if wf_proj is None else dict(wf_proj)
    wfp.update({'nodes': True, '_id': False})
    wfs = []
    for wfn in lpad.workflows.find(wf_query, wfp):
        fwq = {**fw_query, '$expr': {'$in': ['$fw_id', wfn['nodes']]}}
        wfn['nodes'] = list(lpad.fireworks.find(fwq, fw_proj))
        wfs.append(wfn)
    return wfs


if os.environ.get('MONGOMOCK_SERVERSTORE_FILE'):
    get_nodes_info = get_nodes_info_mongomock
else:
    get_nodes_info = get_nodes_info_mongodb


def object_from_file(class_, path):
    """a wrapper function to call various from_file-type class methods"""
    try:
        return class_.from_file(path)
    except tuple(FILE_READ_EXCEPTIONS) as err:  # tuple() to avoid E0712
        raise ObjectFromFileError(path) from err


def retrieve_value(lpad, launch_id, name):
    """retrieve the output value from the FWAction of a given launch"""
    launch_dct = lpad.launches.find_one({'launch_id': launch_id}, {'action': True})
    return load_object(launch_dct['action']['update_spec'][name]).value


def get_vary_df(lpad, uuid):
    """retrieve the vary table from the meta-node"""
    wf_q = {'metadata.uuid': uuid}
    fw_q = {'name': '_fw_meta_node', 'spec._vary': {'$exists': True}}
    fw_p = {'spec._vary': True}
    nodes = next(d['nodes'] for d in get_nodes_info(lpad, wf_q, fw_q, fw_p))
    if nodes:
        assert len(nodes) == 1
        return load_object(nodes[0]['spec']['_vary'])
    return None
