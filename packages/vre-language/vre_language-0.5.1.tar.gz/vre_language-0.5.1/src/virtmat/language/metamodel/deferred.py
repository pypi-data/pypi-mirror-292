"""metamodel manipulations in case of deferred evaluation"""
import uuid
from textx import textx_isinstance, get_children_of_type


def deferred_vartuple_processor(model, metamodel):
    """
    Replace the parameter of VarTuple objects with a GeneralReference in the
    case of deferred evaluation. This is performed to avoid repeated evaluations
    of the right hand side (the parameter) for each VarTuple Variable object.

    Example: This is equivalent to substitute '(a, b) = func(3)' with
    'c = func(3); (a, b) = c' where 'func(x) = (x, 2*x)'

    TODO: it would be nicer to pack (a, b) in a tuple of outputs in tuple_func()
    """
    if not isinstance(model, str):
        model_params = getattr(model, '_tx_model_params')
        if 'deferred_mode' in model_params and model_params['deferred_mode']:
            for vart in get_children_of_type('VarTuple', model):
                if textx_isinstance(vart.parameter, metamodel['Tuple']):
                    for var, par in zip(vart.variables, vart.parameter.params):
                        var.parameter = par
                elif not textx_isinstance(vart.parameter, metamodel['GeneralReference']):
                    var = metamodel['Variable']()
                    setattr(var, 'name', uuid.uuid4().hex)
                    setattr(var, 'parameter', vart.parameter)
                    setattr(var, 'resources', None)
                    setattr(var, 'parent', model)
                    model.statements.append(var)
                    var_ref = metamodel['GeneralReference']()
                    setattr(var_ref, 'ref', var)
                    setattr(var_ref, 'accessors', [])
                    setattr(var_ref, 'parent', vart)
                    setattr(vart, 'parameter', var_ref)
