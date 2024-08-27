# pylint: disable = protected-access
"""
Language interpreter for delayed evaluation

The methods below return the relevant Python functions together with a tuple
with their parameters. The evaluations are performed via delegation.
"""
import pathlib
from itertools import islice, chain
from functools import partial, reduce, cached_property
from operator import gt, lt, eq, ne, le, ge
from operator import add, neg, mul, truediv
from operator import and_, or_, not_, invert
import numpy
import pandas
import pint_pandas
from textx import get_parent_of_type, get_metamodel
from virtmat.language.constraints.imports import get_object_import
from virtmat.language.utilities.textx import isinstance_m
from virtmat.language.utilities.ioops import load_value
from virtmat.language.utilities.formatters import formatter
from virtmat.language.utilities.errors import textxerror_wrap, error_handler
from virtmat.language.utilities.errors import SubscriptingError, PropertyError
from virtmat.language.utilities.errors import InvalidUnitError
from virtmat.language.utilities.types import checktype, checktype_, settype
from virtmat.language.utilities.types import typemap, is_array
from virtmat.language.utilities.types import scalar_numtype, is_array_type
from virtmat.language.utilities.types import is_scalar_type, is_numeric_type
from virtmat.language.utilities.lists import get_array_aslist
from virtmat.language.utilities.units import get_units, get_dimensionality
from virtmat.language.utilities import amml, chemistry
from .instant_executor import program_value, plain_type_value, get_nested_array

# binary operator--function map
binop_map = {'>': gt, '<': lt, '==': eq, '!=': ne, '<=': le, '>=': ge,
             '+': add, '-': lambda x, y: add(x, neg(y)), '*': mul, '/': truediv,
             'or': lambda x, y: x or y, 'and': lambda x, y: x and y,
             'or_': or_, 'and_': and_, '**': pow}


def dummies_right(func, args):
    """reorder arguments so that dummy variables are the end of the list"""
    params = []
    order = []
    for index, arg in enumerate(args):
        if not isinstance_m(arg, ['Dummy']):
            params.append(arg)
            order.append(index)
    for index, arg in enumerate(args):
        if isinstance_m(arg, ['Dummy']):
            params.append(arg)
            order.append(index)
    return lambda *x: func(*[e for i, e in sorted(zip(order, x))]), tuple(params)


def print_func(self):
    """return a 2-tuple containing a function and a list of parameters"""
    func_pars = [par.func for par in self.params]
    funcs = [t[0] for t in func_pars]
    pars = tuple(t[1] for t in func_pars)
    pars_lens = [len(p) for p in pars]

    def retfunc(*args):
        iargs = iter(args)
        pargs = [list(islice(iargs, pl)) for pl in pars_lens]
        values = [formatter(f(*a)) for f, a in zip(funcs, pargs)]
        return ' '.join(values)
    return retfunc, tuple(chain.from_iterable(pars))


def print_parameter_func(self):
    """return a 2-tuple containing a function and a list of parameters"""
    if self.units is None:
        return self.param.func
    units = self.units
    func, pars = self.param.func

    def retfunc(*args):
        val = func(*args)
        if isinstance(val, typemap['Quantity']):
            return val.to(units)
        if isinstance(val, typemap['Series']):
            if isinstance(val.dtype, pint_pandas.PintType):
                return val.pint.to(units)
            assert val.dtype == 'object'
            elems = [elem.to(units) for elem in val]
            name = val.name
            return typemap['Series'](name=name, data=elems, dtype='object')
        if isinstance(val, typemap['FloatArray']):
            val = val.quantity.to(units)
            return typemap['FloatArray'](val.magnitude, val.units)
        assert isinstance(val, typemap['IntArray'])
        assert val.ndim == 1
        return numpy.asarray([el.to(units) for el in val], dtype='object')
    return retfunc, pars


def type_func(self):
    """return a 2-tuple containing a function and a list of parameters"""
    func, pars = self.param.func
    par = self.param
    name = par.ref.name if isinstance_m(par, ['GeneralReference']) else None
    datatype = getattr(getattr(par.type_, 'datatype', None), '__name__', None)
    scalar = is_scalar_type(par.type_)
    numeric = is_numeric_type(par.type_)
    partype = par.type_.__name__

    def retfunc(val):
        dct = {'name': name,
               'type': partype,
               'scalar': scalar,
               'numeric': numeric,
               'datatype': datatype,
               'dimensionality': str(get_dimensionality(val)) if numeric else None,
               'units': str(get_units(val)) if numeric else None}
        return typemap['Table']([dct])
    return (lambda *x: retfunc(func(*x)), pars)


def variable_func(self):
    """return a 2-tuple containing a function and a list of parameters"""
    if isinstance_m(self.parent, ['VarTuple']):
        if isinstance_m(self.parent.parameter, ['GeneralReference']):
            vars_ = self.parent.variables
            index = next(i for i, v in enumerate(vars_) if v == self)
            func, pars = self.parent.parameter.func
            return (lambda *args: func(*args)[index], pars)
        assert isinstance_m(self.parent.parameter, ['Tuple'])
    return self.parameter.func


def quantity_func(self):
    """return a 2-tuple containing a function and a list of parameters"""
    if self.need_input:
        url = self.url
        filename = self.filename
        self.need_input = False
        type_ = self.type_
        return (lambda: checktype_(load_value(url, filename), type_), tuple())
    numval = self.inp_value.value
    magnitude = numpy.nan if numval is None else numval
    pars = (magnitude, self.inp_units)
    return (lambda: typemap['Quantity'](*pars), tuple())


def plain_type_func(self):
    """return a 2-tuple containing a function and a list of parameters"""
    if self.need_input:
        self.need_input = False
        url = self.url
        filename = self.filename
        type_ = self.type_
        return (lambda: checktype_(load_value(url, filename), type_), tuple())
    val = self.value  # evaluate here to allow serialization with dill
    return (lambda: val, tuple())


def series_func(self):
    """return a 2-tuple containing a function and a list of parameters"""
    datatype = self.type_.datatype
    if self.need_input:
        url = self.url
        filename = self.filename
        self.need_input = False
        type_ = self.type_
        return (lambda: checktype_(load_value(url, filename), type_), tuple())
    name = self.name
    if datatype is not None and issubclass(datatype, numpy.ndarray):
        elements = (e.value for e in self.elements)
        elements = (numpy.nan if e is None else e for e in elements)
        elements = [typemap['Quantity'](e, self.inp_units) for e in elements]
        return (lambda: typemap['Series'](data=elements, name=name), tuple())
    if datatype in (complex, int):
        elements = (numpy.nan if e.value is None else e.value for e in self.elements)
        data = [typemap['Quantity'](e, self.inp_units) for e in elements]
        return (lambda: typemap['Series'](data=data, name=name), tuple())
    if datatype is float:
        data = [numpy.nan if e.value is None else e.value for e in self.elements]
        units = self.inp_units if self.inp_units else 'dimensionless'
        dtype = pint_pandas.PintType(units)
        return (lambda: typemap['Series'](data=data, dtype=dtype, name=name), tuple())
    tups = [e.func for e in self.elements]
    funs = [t[0] for t in tups]
    pars = [t[1] for t in tups]
    lens = [len(p) for p in pars]

    def get_series_val(*args):
        iargs = iter(args)
        fargs = [list(islice(iargs, pl)) for pl in lens]
        return typemap['Series']([f(*a) for f, a in zip(funs, fargs)], name=name)

    if datatype is not None and issubclass(datatype, typemap['Quantity']):
        def get_check_series_val(*args):
            ser = get_series_val(*args)
            if len(set(e.units for e in ser)) != 1:
                msg = 'Numeric type series must have elements of the same units.'
                raise InvalidUnitError(msg)
            return ser
        return get_check_series_val, tuple(chain.from_iterable(pars))
    return get_series_val, tuple(chain.from_iterable(pars))


def table_func(self):
    """return a 2-tuple containing a function and a list of parameters"""
    if self.need_input:
        url = self.url
        filename = self.filename
        self.need_input = False
        type_ = self.type_
        return (lambda: checktype_(load_value(url, filename), type_), tuple())

    funcs = [c.func[0] for c in self.columns]
    pars = [c.func[1] for c in self.columns]
    pars_lens = [len(p) for p in pars]

    def get_table_val(*args):
        iargs = iter(args)
        fargs = [list(islice(iargs, pl)) for pl in pars_lens]
        series = [f(*a) for f, a in zip(funcs, fargs)]
        return typemap['Table'](pandas.concat(series, axis=1))
    return (get_table_val, tuple(chain.from_iterable(pars)))


def dict_func(self):
    """return a 2-tuple containing a function and a list of parameters"""

    funcs = [c.func[0] for c in self.values]
    pars = [c.func[1] for c in self.values]
    pars_lens = [len(p) for p in pars]

    def get_dict_val(*args):
        iargs = iter(args)
        fargs = [list(islice(iargs, pl)) for pl in pars_lens]
        dct = dict(zip(self.keys, ([f(*a)] for f, a in zip(funcs, fargs))))
        return pandas.DataFrame.from_dict(dct)
    return (get_dict_val, tuple(chain.from_iterable(pars)))


def tag_func(self):
    """return a 2-tuple containing a function and a list of parameters"""
    return self.tagtab.func


def bool_str_array_func(self):
    """return a 2-tuple containing a function and a list of parameters"""
    if self.url or self.filename:
        url = self.url
        filename = self.filename
        type_ = self.type_
        return (lambda: checktype_(load_value(url, filename), type_), tuple())
    data = get_array_aslist(self.elements)
    return (lambda: numpy.array(data), tuple())


def numeric_array_func(self):
    """return a 2-tuple containing a function and a list of parameters"""
    if self.url or self.filename:
        url = self.url
        filename = self.filename
        type_ = self.type_
        return (lambda: checktype_(load_value(url, filename), type_), tuple())
    data = numpy.array(get_array_aslist(self.elements), dtype=self.type_.datatype)
    units = self.inp_units if self.inp_units else 'dimensionless'
    array = self.type_(data, units)
    return (lambda: array, tuple())


def numeric_subarray_func(self):
    """return a 2-tuple containing a function and a list of parameters"""
    arr = numpy.array(get_array_aslist(self.elements), dtype=self.type_.datatype)
    return (lambda: arr, tuple())


def get_general_reference_func(func, pars, accessor):
    """return a 2-tuple containing a function and a list of parameters"""
    if accessor.index is not None:
        acc_index = accessor.index

        def get_indexed(value):
            try:
                if isinstance(value, typemap['Table']):
                    dfr = value.iloc[[acc_index]]
                    return tuple(next(dfr.itertuples(index=False, name=None)))
                if isinstance(value, typemap['Series']):
                    return value.values[acc_index]
                if is_array(value):
                    return value[acc_index]
                if isinstance(value, amml.AMMLObject):
                    return value[acc_index]
                raise TypeError(f'invalid type {type(value)}')
            except IndexError as err:
                msg = f'{str(err)}: index {acc_index}, length {len(value)}'
                raise SubscriptingError(msg) from err
        return (lambda *x: get_indexed(func(*x)), pars)
    acc_id = accessor.id

    def get_property(value):
        try:
            return value[acc_id]
        except KeyError as err:
            msg = f'property "{acc_id}" not available'
            raise PropertyError(msg) from err
    return (lambda *x: get_property(func(*x)), pars)


def general_reference_func(self):
    """return a 2-tuple containing a function and a list of parameters"""
    def checkref(obj):
        if isinstance_m(obj, ['Variable', 'Dummy', 'ObjectImport']):
            return (lambda x: x, (obj,))
        return obj.func
    func, pars = checkref(self.ref)
    for accessor in self.accessors:
        func, pars = get_general_reference_func(func, pars, accessor)
    return func, pars


def iterable_property_func(self):
    """return a 2-tuple containing a function and a list of parameters"""
    func, pars = self.obj.func
    if hasattr(self, 'name_') and self.name_:
        return (lambda *x: func(*x).name, pars)
    if hasattr(self, 'columns') and self.columns:
        return (lambda *x: func(*x).columns.to_series(name='columns'), pars)
    slice_ = self.slice
    start_ = self.start
    stop_ = self.stop
    step_ = self.step

    def get_sliced_value(value):
        return value[start_:stop_:step_] if slice_ else value

    def get_int_array(arr):
        assert all(isinstance(v.magnitude, int) for v in arr)
        data = numpy.array([v.magnitude for v in arr], dtype='int')
        return typemap['IntArray'](data, next(v.units for v in arr))

    def get_float_array(arr):
        if isinstance(arr, pint_pandas.PintArray):
            return arr.quantity
        assert all(isinstance(v.magnitude, float) for v in arr)
        data = numpy.array([v.magnitude for v in arr], dtype='float')
        return typemap['FloatArray'](data, next(v.units for v in arr))

    if self.array:
        if issubclass(self.obj.type_.datatype, str):
            return (lambda *x: get_sliced_value(func(*x)).values.astype(str), pars)
        if issubclass(self.obj.type_.datatype, bool):
            return (lambda *x: get_sliced_value(func(*x)).values, pars)
        if issubclass(self.obj.type_.datatype, int):
            return (lambda *x: get_int_array(get_sliced_value(func(*x)).values), pars)
        if issubclass(self.obj.type_.datatype, float):
            return (lambda *x: get_float_array(get_sliced_value(func(*x)).values), pars)
        if is_array_type(self.obj.type_.datatype):
            return (lambda *x: get_nested_array(get_sliced_value(func(*x)).values), pars)
        return (lambda *x: get_sliced_value(func(*x)).values, pars)
    return (settype(lambda *x: get_sliced_value(func(*x))), pars)


def iterable_query_func(self):
    """return a 2-tuple containing a function and a list of parameters"""
    func, pars = self.obj.func
    pars = list(pars)
    olens = len(pars)
    where = self.where
    where_all = self.where_all
    where_any = self.where_any
    column_names = self.columns
    if where:
        conds = [self.condition] if self.condition else self.conditions
        cfunc = [c.func[0] for c in conds]
        cpars = [c.func[1] for c in conds]
        clens = [len(p) for p in cpars]
        pars.extend(chain.from_iterable(cpars))
    else:
        cfunc = []
        clens = []

    def get_query_value(*args):
        iargs = iter(args)
        oargs = list(islice(iargs, olens))
        value = func(*oargs)
        if where:
            fargs = [list(islice(iargs, cl)) for cl in clens]
            fconds = [f(*a) for f, a in zip(cfunc, fargs)]
            if where_all:
                val = value[reduce(lambda x, y: x & y, fconds)]
            elif where_any:
                val = value[reduce(lambda x, y: x | y, fconds)]
            else:
                val = value[fconds[0]]
        else:
            val = value
        if column_names:
            val = val[column_names]
        return val.reset_index(drop=True)
    return (get_query_value, tuple(pars))


def condition_in_func(self):
    """return a 2-tuple containing a function and a list of parameters"""
    qobj_ref = get_parent_of_type('IterableQuery', self).obj
    qobj_ref_func, cpars = qobj_ref.func
    column = self.column

    def cfunc(*args):
        val = qobj_ref_func(*args)
        if isinstance(val, pandas.DataFrame):
            return val[column]
        assert val.name == column
        return val

    cpars_len = len(cpars)
    if self.parameter:
        pfunc, ppars = self.parameter.func

        def retfunc_par(*args):
            return cfunc(*args[:cpars_len]).isin(pfunc(*args[cpars_len:]))
        return (retfunc_par, (*cpars, *ppars))
    pfunc = [p.func[0] for p in self.params]
    ppars = tuple(p.func[1] for p in self.params)
    ppars_lens = [len(p) for p in ppars]

    def retfunc_pars(*args):
        iargs = iter(args)
        cargs = list(islice(iargs, cpars_len))
        pargs = [list(islice(iargs, pl)) for pl in ppars_lens]
        return cfunc(*cargs).isin([f(*a) for f, a in zip(pfunc, pargs)])
    return (retfunc_pars, tuple(chain.from_iterable((cpars,)+ppars)))


def condition_comparison_func(self):
    """return a 2-tuple containing a function and a list of parameters"""
    assert self.operand_left is None
    assert self.column_left is not None
    operator = binop_map[self.operator]
    qobj_ref = get_parent_of_type('IterableQuery', self).obj
    qobj_func, qobj_pars = qobj_ref.func
    qobj_parlen = len(qobj_pars)
    if self.operand_right:
        opr_func, opr_pars = self.operand_right.func
    left = self.column_left
    if issubclass(qobj_ref.type_, typemap['Table']):
        if self.column_right:
            right = self.column_right

            def two_columns(*args):
                val = qobj_func(*args)
                return operator(val[left], val[right])
            return two_columns, qobj_pars
        if self.operand_right:

            def table_column_operand(*args):
                val = qobj_func(*args[0:qobj_parlen])
                return operator(val[left], opr_func(*args[qobj_parlen:]))
            return table_column_operand, (*qobj_pars, *opr_pars)
    assert issubclass(qobj_ref.type_, typemap['Series'])

    def series_operand(*args):
        val = qobj_func(*args[0:qobj_parlen])
        assert val.name == left
        return operator(val, opr_func(*args[qobj_parlen:]))
    return series_operand, (*qobj_pars, *opr_pars)


def range_func(self):
    """return a 2-tuple containing a function and a list of parameters"""
    tup = (self.start, self.stop, self.step)
    tups = [t.func for t in tup]
    funcs = [t[0] for t in tups]
    pars = [t[1] for t in tups]
    lens = [len(t[1]) for t in tups]
    name = self.parent.name if hasattr(self.parent, 'name') else None

    def get_range_val(*args):
        iargs = iter(args)
        fargs = [list(islice(iargs, pl)) for pl in lens]
        cargs = [f(*a) for f, a in zip(funcs, fargs)]
        unit = cargs[0].units
        data = numpy.arange(cargs[0].magnitude, cargs[1].to(unit).magnitude,
                            cargs[2].to(unit).magnitude).tolist()
        # redundant code with series, instant executor
        if all(isinstance(e, int) for e in data):
            data = (typemap['Quantity'](e, unit) for e in data)
            dtype = 'object'
        else:
            assert all(isinstance(e, float) for e in data)
            dtype = pint_pandas.PintType(unit)
        return typemap['Series'](data=data, name=name, dtype=dtype)
    return (get_range_val, tuple(chain.from_iterable(pars)))


def map_func(self):
    """return a 2-tuple containing a function and a list of parameters"""
    name = self.parent.name if hasattr(self.parent, 'name') else None
    func_def = self.lambda_ if self.lambda_ else self.function
    if not isinstance_m(func_def, ['ObjectImport']):
        nfunc, npars = dummies_right(*func_def.expr.func)
        func_args = func_def.args
    else:
        nfunc = get_object_import(self.function)
        dummy = get_metamodel(self)['Dummy']
        dummy.name = None
        npars = (dummy,)*len(self.params)
        func_args = npars
    func_pars = [p.func for p in self.params]
    plen = sum(not isinstance_m(p, ['Dummy']) for p in npars)
    dummy_funcs = []
    dummy_pars_lens = []
    all_pars = [npars[:plen]]
    for par in npars[plen:]:
        ind = next(i for i, a in enumerate(func_args) if a.name == par.name)
        dummy_funcs.append(func_pars[ind][0])
        all_pars.append(func_pars[ind][1])
        dummy_pars_lens.append(len(func_pars[ind][1]))

    def get_map_val(*args):
        iargs = iter(args)
        pargs = list(islice(iargs, plen))
        dargs = [list(islice(iargs, pl)) for pl in dummy_pars_lens]
        iterables = [f(*a) for f, a in zip(dummy_funcs, dargs)]
        return typemap['Series'](map(partial(nfunc, *pargs), *iterables), name=name)
    return get_map_val, tuple(chain.from_iterable(all_pars))


def filter_func(self):
    """return a 2-tuple containing a function and a list of parameters"""
    name = self.parent.name if hasattr(self.parent, 'name') else None
    func_def = self.lambda_ if self.lambda_ else self.function
    if not isinstance_m(func_def, ['ObjectImport']):
        nfunc, npars = dummies_right(*func_def.expr.func)
    else:
        nfunc = get_object_import(self.function)
        npars = (get_metamodel(self)['Dummy'],)
    pfun, pars = self.parameter.func
    plen = sum(not isinstance_m(p, ['Dummy']) for p in npars)
    all_pars = npars[:plen] + pars
    dlen = len(npars[plen:])

    def get_filter_val(*args):
        filter_f = partial(lambda *x: nfunc(*x[:plen], *x[plen:]*dlen), *args[:plen])
        filter_d = pfun(*args[plen:]).dropna()  # alt: lambda *x: not(pandas.isna(filter_f(*x)))
        return typemap['Series'](filter(filter_f, filter_d), name=name)
    return get_filter_val, all_pars


def reduce_func(self):
    """return a 2-tuple containing a function and a list of parameters"""
    func_def = self.lambda_ if self.lambda_ else self.function
    pfun, pars = self.parameter.func
    if not isinstance_m(func_def, ['ObjectImport']):
        nfunc, npars = dummies_right(*func_def.expr.func)
        plen = sum(not isinstance_m(p, ['Dummy']) for p in npars)
        npars_u = npars[:plen] + tuple(func_def.args)
        mapping = [next(i for i, a in enumerate(npars_u) if a.name == p.name) for p in npars]

        def nfunc_u(*args):
            return partial(lambda *x: nfunc(*[x[i] for i in mapping]), *args)
        apars = npars[:plen] + pars
        return lambda *x: reduce(nfunc_u(*x[:plen]), pfun(*x[plen:])), apars
    nfunc = get_object_import(self.function)
    return lambda *x: reduce(nfunc, pfun(*x)), pars


def func_reduce_func(self, func):
    """return a 2-tuple containing a function and a list of parameters"""
    if self.parameter:
        pfun, pars = self.parameter.func
        retfunc = (lambda *x: func(pfun(*x)), pars)
    else:
        tuples = [p.func for p in self.params]
        funcs = [t[0] for t in tuples]
        pars = [t[1] for t in tuples]
        pars_lens = [len(p) for p in pars]

        def get_func_reduce_val(*args):
            iargs = iter(args)
            fargs = [list(islice(iargs, pl)) for pl in pars_lens]
            return func([f(*a) for f, a in zip(funcs, fargs)])
        retfunc = (get_func_reduce_val, tuple(chain.from_iterable(pars)))
    return retfunc


def in_func(self):
    """return a 2-tuple containing a function and a list of parameters"""
    if self.parameter:
        func_x, pars_x = self.element.func
        func_y, pars_y = self.parameter.func
        len_x = len(pars_x)
        retfunc = (lambda *args: func_x(*args[:len_x]) in func_y(*args[len_x:]).values,
                   (*pars_x, *pars_y))
    else:
        elem_func, elem_pars = self.element.func
        elem_pars_len = len(elem_pars)
        func_pars = [p.func for p in self.params]
        funcs = [t[0] for t in func_pars]
        pars = tuple(t[1] for t in func_pars)
        pars_lens = [len(p) for p in pars]

        def get_in_val(*args):
            iargs = iter(args)
            eargs = list(islice(iargs, elem_pars_len))
            pargs = [list(islice(iargs, pl)) for pl in pars_lens]
            return elem_func(*eargs) in [f(*a) for f, a in zip(funcs, pargs)]
        retfunc = (get_in_val, tuple(chain.from_iterable(elem_pars+pars)))
    return retfunc


def binop_func(func, ops, from_the_left=True):
    """binary operator as a 2-tuple with a function and parameters"""
    if len(ops) == 0:
        retval = func
    else:
        operator, operand = ops.pop(0) if from_the_left else ops.pop(-1)
        left_func, left_pars = func if from_the_left else operand.func
        right_func, right_pars = operand.func if from_the_left else func
        pars = left_pars + right_pars
        operator = binop_map[operator]
        left_pars_length = len(left_pars)
        retval = binop_func(
            (
                lambda *args: operator(left_func(*args[0:left_pars_length]),
                                       right_func(*args[left_pars_length:])),
                pars
            ),
            ops, from_the_left=from_the_left)
    return retval


def expression_func(self):
    """return a 2-tuple containing a function and a list of parameters"""
    func = self.operands[0].func
    ops = list(zip(self.operators, self.operands[1:]))
    retfunc = binop_func(func, ops)
    return retfunc


def term_func(self):
    """return a 2-tuple containing a function and a list of parameters"""
    func = self.operands[0].func
    ops = list(zip(self.operators, self.operands[1:]))
    retfunc = binop_func(func, ops)
    return retfunc


def factor_func(self):
    """return a 2-tuple containing a function and a list of parameters"""
    func = self.operands[-1].func
    operators = ['**']*(len(self.operands)-1)
    ops = list(zip(operators, self.operands[:-1]))
    retfunc = binop_func(func, ops, from_the_left=False)
    return retfunc


def power_func(self):
    """return a 2-tuple containing a function and a list of parameters"""
    func, pars = self.operand.func
    if self.sign == '-':
        retfunc = (lambda *args: -func(*args), pars)
    else:
        retfunc = (func, pars)
    return retfunc


def operand_func(self):
    """return a 2-tuple containing a function and a list of parameters"""
    return self.operand.func


def binary_operation_func(self, operator):
    """return a 2-tuple containing a function and a list of parameters"""
    func = self.operands[0].func
    ops = list(zip([operator]*len(self.operands[1:]), self.operands[1:]))
    retfunc = binop_func(func, ops)
    return retfunc


def not_func(self, operator):
    """return a 2-tuple containing a function and a list of parameters"""
    retfunc = self.operand.func
    if self.not_:
        func, pars = retfunc
        retfunc = (lambda *args: operator(func(*args)), pars)
    return retfunc


def comparison_func(self):
    """return a 2-tuple containing a function and a list of parameters"""
    lfunc, lpars = self.left.func
    rfunc, rpars = self.right.func
    all_pars = (*lpars, *rpars)
    lparslen = len(lpars)
    operator = self.operator
    type_ = self.type_

    def get_comparison_val(*args):
        lval = lfunc(*args[:lparslen])
        rval = rfunc(*args[lparslen:])
        for operand in (lval, rval):
            if isinstance(operand, typemap['Quantity']):
                assert isinstance(operand.magnitude, (*scalar_numtype, type(pandas.NA)))
                if isinstance(operand.magnitude, complex):
                    assert operator in ('==', '!=')
            else:
                assert isinstance(operand, (bool, str))
                assert operator in ('==', '!=')
        return type_(binop_map[operator](lval, rval))
    return get_comparison_val, all_pars


def real_func(self):
    """return a 2-tuple containing a function and a list of parameters"""
    func, pars = self.parameter.func
    return (lambda *args: func(*args).real, pars)


def imag_func(self):
    """return a 2-tuple containing a function and a list of parameters"""
    func, pars = self.parameter.func
    return (lambda *args: func(*args).imag, pars)


def if_expression_func(self):
    """
    Naive implementation: condition and the active branch are executed serially
    on the same resources
    """
    expr_func, expr_pars = self.expr.func
    expr_pars_len = len(expr_pars)
    true_b, true_b_pars = self.true_.func
    true_b_pars_len = expr_pars_len + len(true_b_pars)
    false_b, false_b_pars = self.false_.func

    def iffunc(*args):
        if expr_func(*args[:expr_pars_len]):
            retval = true_b(*args[expr_pars_len:true_b_pars_len])
        else:
            retval = false_b(*args[true_b_pars_len:])
        return retval
    retfunc = (iffunc, (*expr_pars, *true_b_pars, *false_b_pars))
    return retfunc


def function_call_func(self):
    """return a 2-tuple containing a function and a list of parameters"""
    if isinstance_m(self.function, ['ObjectImport']):
        obj = get_object_import(self.function)
        assert callable(obj)
        func_pars = [p.func for p in self.params]
        pars = [pars for func, pars in func_pars]
        funcs = [func for func, pars in func_pars]
        lens = list(map(len, pars))
        pars_flat = tuple(p for par in pars for p in par)

        def fcall_func(*args):
            iter_args = iter(args)
            fcall_args = [list(islice(iter_args, i)) for i in lens]
            return obj(*[f(*a) for f, a in zip(funcs, fcall_args)])
        retfunc = (settype(fcall_func), pars_flat)
    else:
        assert isinstance_m(self.function, ['FunctionDefinition'])
        if not get_parent_of_type('FunctionDefinition', self):
            retfunc = self.expr.func
        else:
            # function call in a function definition, e.g. f(x) = 2*g(x)
            retfunc = None
    return retfunc


def object_import_func(self):
    """return a 2-tuple containing a function and a list of parameters"""
    obj = get_object_import(self)
    assert not callable(obj)
    return (settype(lambda: obj), tuple())


def tuple_func(self):
    """return a 2-tuple containing a function and a list of parameters"""
    tuple_pars = [p.func for p in self.params]
    tpars = [pars for func, pars in tuple_pars]
    funcs = [func for func, pars in tuple_pars]
    tlens = [len(pars) for func, pars in tuple_pars]

    def get_tuple_val(*args):
        iter_args = iter(args)
        targs = [list(islice(iter_args, t)) for t in tlens]
        return tuple(f(*a) for f, a in zip(funcs, targs))
    return (get_tuple_val, tuple(chain.from_iterable(tpars)))


def amml_structure_func(self):
    """return a 2-tuple containing a function and a list of parameters"""
    if self.filename or self.url:
        url = self.url
        type_ = self.type_
        filename = self.filename
        suffix = pathlib.Path(filename).suffix
        if filename and suffix not in ['.yml', '.yaml', '.json']:
            return (lambda: amml.AMMLStructure.from_ase_file(filename), tuple())
        return (lambda: checktype_(load_value(url, filename), type_), tuple())
    func, pars = self.tab.func
    name = self.name
    return (lambda *x: amml.AMMLStructure(func(*x), name), pars)


def amml_calculator_func(self):
    """return a 2-tuple containing a function and a list of parameters"""
    name = self.name
    pinning = self.pinning
    version = self.version
    task = self.task
    if self.parameters is None:
        return lambda: amml.Calculator(name, pandas.DataFrame(), pinning, version, task), tuple()
    func, pars = self.parameters.func
    return lambda *x: amml.Calculator(name, func(*x), pinning, version, task), pars


def amml_algorithm_func(self):
    """return a 2-tuple containing a function and a list of parameters"""
    name = self.name
    m2o = self.many_to_one
    if self.parameters is None:
        return (lambda: amml.Algorithm(name, pandas.DataFrame(), m2o), tuple())
    func, pars = self.parameters.func
    return (lambda *x: amml.Algorithm(name, func(*x), m2o), pars)


def amml_property_func(self):
    """return a 2-tuple containing a function and a list of parameters"""
    sfunc, spars = self.struct.func
    cfunc, cpars = self.calc.func if self.calc else (lambda: None, tuple())
    afunc, apars = self.algo.func if self.algo else (lambda: None, tuple())
    props = self.names
    cpl = len(cpars)
    spl = len(spars)
    apl = len(apars)
    constr_tuples = [c.func for c in self.constrs]
    constr_func = [f for f, p in constr_tuples]
    constr_pars = [p for f, p in constr_tuples]
    constr_pars_lens = [len(p) for p in constr_pars]
    pars = (spars, cpars, apars, *constr_pars)

    def get_property_val(*args):
        iargs = iter(args)
        struct_args = list(islice(iargs, spl))
        calc_args = list(islice(iargs, cpl))
        algo_args = list(islice(iargs, apl))
        constr_args = [list(islice(iargs, pl)) for pl in constr_pars_lens]
        constrs = [f(*x) for f, x in zip(constr_func, constr_args)]
        return amml.Property(props, sfunc(*struct_args), calculator=cfunc(*calc_args),
                             algorithm=afunc(*algo_args), constraints=constrs)
    return (get_property_val, tuple(chain.from_iterable(pars)))


def amml_constraint_func(self):
    """return a 2-tuple containing a function and a list of parameters"""
    name = self.name
    fixed_func, fixed_pars = self.fixed.func
    if self.direction is None:
        return (lambda *x: amml.Constraint(name, fixed=fixed_func(*x)), fixed_pars)
    fpl = len(fixed_pars)
    direc_func, direc_pars = self.direction.func
    pars = (*fixed_pars, *direc_pars)
    return (lambda *x: amml.Constraint(name, fixed=fixed_func(*x[:fpl]),
                                       direction=direc_func(*x[fpl:])), pars)


def chem_reaction_func(self):
    """return a 2-tuple containing a function and a list of parameters"""
    species = [term.species.func for term in self.educts+self.products]
    func_spec = [t[0] for t in species]
    pars_spec = tuple(t[1] for t in species)
    pars_lens = [len(p) for p in pars_spec]
    coeffs = []
    for term in self.educts:
        coeffs.append(-term.coefficient)
    for term in self.products:
        coeffs.append(term.coefficient)

    if self.props is None:
        props_avail = False
        func_props = None
        pars_all = tuple(chain.from_iterable(pars_spec))
    else:
        props_avail = True
        func_props, pars_props = self.props.func
        pars_all = tuple(chain.from_iterable(pars_spec)) + pars_props

    def get_chem_reaction(*args):
        iargs = iter(args)
        pargs = [list(islice(iargs, pl)) for pl in pars_lens]
        specs = [f(*a) for f, a in zip(func_spec, pargs)]
        terms = [{'coefficient': c, 'species': s} for c, s in zip(coeffs, specs)]
        props = func_props(*list(iargs)) if props_avail else None
        return chemistry.ChemReaction(terms, props)
    return get_chem_reaction, pars_all


def chem_species_func(self):
    """return a 2-tuple containing a function and a list of parameters"""
    name = self.name
    none_func = (lambda: None, tuple())
    comp_f, comp_p = self.composition.func if self.composition else none_func
    props_f, props_p = self.props.func if self.props else none_func
    comp_plen = len(comp_p)
    return (lambda *x: chemistry.ChemSpecies(name, comp_f(*x[:comp_plen]),
                                             props_f(*x[comp_plen:])),
            tuple(chain.from_iterable((comp_p, props_p))))


def add_func_properties(metamodel):
    """Add class properties using monkey style patching"""
    mapping_dict = {
        'Print': print_func,
        'PrintParameter': print_parameter_func,
        'Type': type_func,
        'Variable': variable_func,
        'GeneralReference': general_reference_func,
        'String': plain_type_func,
        'Bool': plain_type_func,
        'Quantity': quantity_func,
        'Power': power_func,
        'Factor': factor_func,
        'Term': term_func,
        'Expression': expression_func,
        'Operand': operand_func,
        'BooleanOperand': operand_func,
        'And': partial(binary_operation_func, operator='and'),
        'Or': partial(binary_operation_func, operator='or'),
        'Not': partial(not_func, operator=not_),
        'Comparison': comparison_func,
        'Real': real_func,
        'Imag': imag_func,
        'IfFunction': if_expression_func,
        'IfExpression': if_expression_func,
        'FunctionCall': function_call_func,
        'Lambda': lambda x: x.expr.func,
        'FunctionDefinition': lambda x: x.expr.func,
        'ObjectImport': object_import_func,
        'Tuple': tuple_func,
        'Series': series_func,
        'Table': table_func,
        'Dict': dict_func,
        'Tag': tag_func,
        'BoolArray': bool_str_array_func,
        'StrArray': bool_str_array_func,
        'IntArray': numeric_array_func,
        'FloatArray': numeric_array_func,
        'ComplexArray': numeric_array_func,
        'IntSubArray': numeric_subarray_func,
        'FloatSubArray': numeric_subarray_func,
        'ComplexSubArray': numeric_subarray_func,
        'IterableProperty': iterable_property_func,
        'IterableQuery': iterable_query_func,
        'ConditionIn': condition_in_func,
        'ConditionComparison': condition_comparison_func,
        'ConditionOr': partial(binary_operation_func, operator='or_'),
        'ConditionAnd': partial(binary_operation_func, operator='and_'),
        'ConditionNot': partial(not_func, operator=invert),
        'Range': range_func,
        'In': in_func,
        'Any': partial(func_reduce_func, func=any),
        'All': partial(func_reduce_func, func=all),
        'Sum': partial(func_reduce_func, func=sum),
        'Map': map_func,
        'Filter': filter_func,
        'Reduce': reduce_func,
        'AMMLStructure': amml_structure_func,
        'AMMLCalculator': amml_calculator_func,
        'AMMLAlgorithm': amml_algorithm_func,
        'AMMLProperty': amml_property_func,
        'AMMLConstraint': amml_constraint_func,
        'ChemReaction': chem_reaction_func,
        'ChemSpecies': chem_species_func
    }
    for key, function_ptr in mapping_dict.items():
        metamodel[key].func = cached_property(function_ptr)
        metamodel[key].func.__set_name__(metamodel[key], 'func')


@checktype
def func_value(self):
    """evaluate a python function object"""
    func, pars = self.func
    return func(*[p.value for p in pars])


def add_deferred_value_properties(metamodel):
    """Add class properties using monkey style patching"""
    mapping_dict = {
        # reused from instant executor
        'Program': program_value,
        'String': plain_type_value,
        'Bool': plain_type_value,
        # deferred evaluation via a python function object
        'Quantity': func_value,
        'PrintParameter': func_value,
        'Type': func_value,
        'Variable': func_value,
        'Power': func_value,
        'Factor': func_value,
        'Term': func_value,
        'Expression': func_value,
        'Operand': func_value,
        'BooleanOperand': func_value,
        'And': func_value,
        'Or': func_value,
        'Not': func_value,
        'Comparison': func_value,
        'IfFunction': func_value,
        'IfExpression': func_value,
        'FunctionCall': func_value,
        'ObjectImport': func_value,
        'Tuple': func_value,
        'Series': func_value,
        'Table': func_value,
        'BoolArray': func_value,
        'StrArray': func_value,
        'IntArray': func_value,
        'FloatArray': func_value,
        'ComplexArray': func_value,
        'IntSubArray': func_value,
        'FloatSubArray': func_value,
        'ComplexSubArray': func_value,
        'IterableProperty': func_value,
        'IterableQuery': func_value,
        'ConditionIn': func_value,
        'ConditionComparison': func_value,
        'ConditionOr': func_value,
        'ConditionAnd': func_value,
        'ConditionNot': func_value,
        'Range': func_value,
        'In': func_value,
        'Any': func_value,
        'All': func_value,
        'Sum': func_value,
        'Map': func_value,
        'Filter': func_value,
        'Reduce': func_value,
        'AMMLStructure': func_value,
        'AMMLCalculator': func_value,
        'AMMLAlgorithm': func_value,
        'AMMLProperty': func_value,
        'AMMLConstraint': func_value,
        'ChemReaction': func_value,
        'ChemSpecies': func_value
    }
    for key, func in mapping_dict.items():
        metamodel[key].value = cached_property(textxerror_wrap(func))
        metamodel[key].value.__set_name__(metamodel[key], 'value')
    metamodel['Print'].value = property(error_handler(textxerror_wrap(func_value)))
