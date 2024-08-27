"""input/output processors"""
from textx import get_children_of_type
from virtmat.language.utilities.errors import textxerror_wrap
from virtmat.language.utilities.ioops import store_value
from virtmat.language.utilities.serializable import get_serializable


@textxerror_wrap
def object_to(obj):
    """Store an object to file or url"""
    store_value(get_serializable(obj.ref.parameter.value), obj.url, obj.filename)


def output_processor(model, _):
    """store objects to files or urls"""
    for obj in get_children_of_type('ObjectTo', model):
        object_to(obj)
