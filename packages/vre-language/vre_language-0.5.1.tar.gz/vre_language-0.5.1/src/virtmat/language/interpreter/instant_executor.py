# pylint: disable=protected-access
"""
Language interpreter for immediate local evaluation using python
"""
import pathlib
from operator import gt, lt, eq, ne, le, ge, not_, invert, and_, or_
from functools import partial, reduce, cached_property
import pandas
import numpy
import pint_pandas
from textx import get_children_of_type, get_parent_of_type
from virtmat.language.constraints.imports import get_object_import
from virtmat.language.metamodel.function import subst
from virtmat.language.utilities.textx import isinstance_m
from virtmat.language.utilities.formatters import formatter
from virtmat.language.utilities.errors import textxerror_wrap, error_handler
from virtmat.language.utilities.errors import SubscriptingError, PropertyError
from virtmat.language.utilities.errors import InvalidUnitError
from virtmat.language.utilities.types import typemap, settype, checktype, checktype_
from virtmat.language.utilities.types import scalar_numtype, is_array, DType
from virtmat.language.utilities.types import is_numeric_type, is_array_type
from virtmat.language.utilities.types import is_scalar_type, is_numeric
from virtmat.language.utilities.lists import get_array_aslist
from virtmat.language.utilities.units import get_units, get_dimensionality
from virtmat.language.utilities.ioops import load_value
from virtmat.language.utilities import amml, chemistry

comp_operators = ('>', '<', '==', '!=', '<=', '>=')
comp_functions = (gt, lt, eq, ne, le, ge)
comp_map = dict(zip(comp_operators, comp_functions))


def is_active_branch(obj):
    """
    Determine whether an object is in an active branch
    Args:
        obj (object): either a statement, a function or an expression
    Returns:
        ret (bool): True if obj in an active branch otherwise False
    """
    if isinstance_m(obj.parent, ['IfFunction', 'IfExpression']):
        par = obj.parent
        ret = (par.true_ if par.expr.value else par.false_) is obj
    else:
        ret = True
    return ret


def program_value(self):
    """Evaluate print objects in the order of occurence"""
    vals = [p.value for p in get_children_of_type('Print', self) if p.value]
    return '\n'.join(vals)


def variable_value(self):
    """Evaluate a variable"""
    if isinstance_m(self.parent, ['VarTuple']):
        vars_ = self.parent.variables
        vals_ = self.parent.value
        ret = next(val for var, val in zip(vars_, vals_) if var == self)
    else:
        ret = self.parameter.value if is_active_branch(self) else None
    return ret


def expression_value(self):
    """Evaluate an arithmetic expression"""
    if is_active_branch(self):
        value = self.operands[0].value
        for operation, operand in zip(self.operators, self.operands[1:]):
            if operation == '+':
                value += operand.value
            else:
                value -= operand.value
        ret = value
    else:
        ret = None
    return ret


def term_value(self):
    """Evaluate a term"""
    value = self.operands[0].value
    for operation, operand in zip(self.operators, self.operands[1:]):
        if operation == '*':
            value *= operand.value
        else:
            value /= operand.value
    return value


def factor_value(self):
    """Evaluate a factor"""
    value = self.operands[-1].value
    for operand in self.operands[-2::-1]:
        value = operand.value**value
    return value


def power_value(self):
    """Evaluate a power"""
    value = self.operand.value
    return -value if self.sign == '-' else value


def operand_value(self):
    """Evaluate an operand"""
    return self.operand.value


def binary_operation_value(self, operator):
    """Evaluate binary operation expression"""
    return reduce(operator, (o.value for o in self.operands))


def not_value(self, operator):
    """Evaluate NOT expression"""
    return operator(self.operand.value) if self.not_ else self.operand.value


@property
@error_handler
@textxerror_wrap
def print_value(self):
    """Evaluate the print function"""
    return ' '.join(formatter(par.value) for par in self.params)


def print_parameter_value(self):
    """Evaluate the print parameter"""
    if self.units is None:
        return self.param.value
    if isinstance(self.param.value, typemap['Quantity']):
        return self.param.value.to(self.units)
    if isinstance(self.param.value, typemap['Series']):
        if isinstance(self.param.value.dtype, pint_pandas.PintType):
            return self.param.value.pint.to(self.units)
        if self.param.value.dtype == 'object':
            elems = [elem.to(self.units) for elem in self.param.value]
            name = self.param.value.name
            return typemap['Series'](name=name, data=elems, dtype='object')
    if isinstance(self.param.value, typemap['FloatArray']):
        val = self.param.value.quantity.to(self.units)
        return typemap['FloatArray'](val.magnitude, val.units)
    assert isinstance(self.param.value, typemap['IntArray'])
    assert self.param.value.ndim == 1
    val = [el.to(self.units) for el in self.param.value]
    return numpy.asarray(val, dtype='object')


def type_value(self):
    """Evaluate the type function"""
    par = self.param
    name = par.ref.name if isinstance_m(par, ['GeneralReference']) else None
    datatype = getattr(getattr(par.type_, 'datatype', None), '__name__', None)
    numeric = is_numeric_type(par.type_)
    dimensionality = str(get_dimensionality(par.value)) if numeric else None
    dct = {'name': name,
           'type': par.type_.__name__,
           'scalar': is_scalar_type(par.type_),
           'numeric': numeric,
           'datatype': datatype,
           'dimensionality': dimensionality,
           'units': str(get_units(par.value)) if numeric else None}
    return typemap['Table']([dct])


def if_expression_value(self):
    """Evaluate an if-expression object, returns the expression value"""
    return self.true_.value if self.expr.value else self.false_.value


def comparison_value(self):
    """Evaluate a comparison expression object"""
    for operand in (self.left.value, self.right.value):
        if isinstance(operand, typemap['Quantity']):
            assert isinstance(operand.magnitude, (*scalar_numtype, type(pandas.NA)))
            if isinstance(operand.magnitude, complex):
                assert self.operator in ('==', '!=')
        else:
            assert isinstance(operand, (bool, str))
            assert self.operator in ('==', '!=')
    return bool(comp_map[self.operator](self.left.value, self.right.value))


@settype
def object_import_value(self):
    """Evaluate an imported non-callable object"""
    obj = get_object_import(self)
    assert not callable(obj)
    return obj


@settype
def function_call_value(self):
    """Evaluate a function_call object"""
    if isinstance_m(self.function, ['ObjectImport']):
        obj = get_object_import(self.function)
        assert callable(obj)
        par_values = [p.value for p in self.params]
        ret = obj(*par_values)
    else:
        assert isinstance_m(self.function, ['FunctionDefinition'])
        if not get_parent_of_type('FunctionDefinition', self):
            ret = self.expr.value
        else:
            ret = None
    return ret


def tuple_value(self):
    """Evaluate a tuple object"""
    return tuple(param.value for param in self.params)


def series_value(self):
    """Evaluate a series object"""
    datatype = self.type_.datatype
    if self.need_input:
        retval = checktype_(load_value(self.url, self.filename), self.type_)
        self.need_input = False
    elif datatype is not None and issubclass(datatype, numpy.ndarray):
        elements = (e.value for e in self.elements)
        if all(is_numeric_type(e.type_) for e in self.elements):
            elements = (numpy.nan if e is None else e for e in elements)
            elements = (typemap['Quantity'](e, self.inp_units) for e in elements)
        retval = typemap['Series'](name=self.name, data=elements)
    else:
        elements = (e if isinstance(e, scalar_numtype) else e.value for e in self.elements)
        if datatype in (int, complex):
            n_elems = (numpy.nan if e is None else e for e in elements)
            elements = (typemap['Quantity'](e, self.inp_units) for e in n_elems)
            dtype = 'object'
        elif datatype is float:
            units = self.inp_units if self.inp_units else 'dimensionless'
            dtype = pint_pandas.PintType(units)
        elif datatype is not None and issubclass(datatype, typemap['Quantity']):
            elements = list(elements)
            if len(set(e.units for e in elements)) != 1:
                msg = 'Numeric type series must have elements of the same units.'
                raise InvalidUnitError(msg)
            dtype = 'object'
        else:
            dtype = None
        retval = typemap['Series'](name=self.name, data=elements, dtype=dtype)
    return retval


def table_value(self):
    """Evaluate a table object"""
    if self.need_input:
        retval = checktype_(load_value(self.url, self.filename), self.type_)
        self.need_input = False
    else:
        retval = pandas.concat((c.value for c in self.columns), axis=1)
    return retval


def dict_value(self):
    """evaluate dictionary value"""
    dct = dict(zip(self.keys, ([v.value] for v in self.values)))
    return pandas.DataFrame.from_dict(dct)


def tag_value(self):
    """evaluate tag value"""
    return self.tagtab.value


def bool_str_array_value(self):
    """evaluate an array object of datatypes bool and str"""
    if self.url or self.filename:
        return checktype_(load_value(self.url, self.filename), self.type_)
    return numpy.array(get_array_aslist(self.elements))


def numeric_array_value(self):
    """evaluate an array object of numeric datatype"""
    if self.url or self.filename:
        return checktype_(load_value(self.url, self.filename), self.type_)
    data = numpy.array(get_array_aslist(self.elements), dtype=self.type_.datatype)
    units = self.inp_units if self.inp_units else 'dimensionless'
    return self.type_(data, units)


def numeric_subarray_value(self):
    """evaluate a subarray object of numeric datatype"""
    return numpy.array(get_array_aslist(self.elements), dtype=self.type_.datatype)


def get_nested_array(arr):
    """normalize array of n-dimensional arrays to n+1 dimensional arrays"""
    assert isinstance(arr, numpy.ndarray)
    float_arr_types = (typemap['Quantity'], numpy.ndarray)
    assert all(isinstance(el, float_arr_types) for el in arr)
    if is_numeric(arr):
        data = []
        for elem in arr:
            magn, units = elem.magnitude, elem.units
            if isinstance(magn, numpy.ndarray):
                magn = magn.tolist()
            data.append(magn)
        return typemap['Quantity'](numpy.array(data), units)
    return numpy.array(elem.tolist() for elem in arr)


@settype
def get_sliced_value(obj):
    """return a value slice of an iterable/sequence data structure object"""
    value = obj.obj.value
    if obj.slice:
        value = value[obj.start:obj.stop:obj.step]
    if obj.array:
        array = value.values
        if isinstance(array, pint_pandas.PintArray):
            return array.quantity
        if isinstance(array, numpy.ndarray):
            if is_array_type(obj.obj.type_.datatype):
                return get_nested_array(array)
            if issubclass(obj.obj.type_.datatype, str):
                return array.astype(str)
            if issubclass(obj.obj.type_.datatype, bool):
                return array
            if issubclass(obj.obj.type_.datatype, int):
                data = numpy.array([v.magnitude for v in array], dtype='int')
                return typemap['IntArray'](data, next(v.units for v in array))
            assert issubclass(obj.obj.type_.datatype, float)
            data = numpy.array([v.magnitude for v in array], dtype='float')
            return typemap['FloatArray'](data, next(v.units for v in array))
        raise TypeError('unknown type')
    return value


@settype
def general_reference_value(self):
    """Evaluate a reference with a list of optional data accessors"""
    retval = self.ref.value
    for accessor in self.accessors:
        if accessor.index is not None:
            try:
                if isinstance(retval, typemap['Table']):
                    dfr = retval.iloc[[accessor.index]]
                    retval = tuple(next(dfr.itertuples(index=False, name=None)))
                elif isinstance(retval, typemap['Series']):
                    retval = retval.values[accessor.index]
                elif is_array(retval):
                    retval = retval[accessor.index]
                elif isinstance(retval, (amml.AMMLObject, chemistry.ChemBase)):
                    retval = retval[accessor.index]
                else:
                    raise TypeError(f'invalid type {type(retval)}')
            except IndexError as err:
                msg = f'{str(err)}: index {accessor.index}, length {len(retval)}'
                raise SubscriptingError(msg) from err
        else:
            try:
                if isinstance(retval, (typemap['Table'], typemap['Series'])):
                    retval = retval[accessor.id]
                elif isinstance(retval, (amml.AMMLObject, chemistry.ChemBase)):
                    retval = retval[accessor.id]
                else:
                    raise TypeError(f'invalid type {type(retval)}')
            except KeyError as err:
                msg = f'property "{accessor.id}" not available'
                raise PropertyError(msg) from err
    return retval


def iterable_property_value(self):
    """Evaluate an iterable property object"""
    if hasattr(self, 'name_') and self.name_:
        ret = self.obj.value.name
    elif hasattr(self, 'columns') and self.columns:
        ret = self.obj.value.columns.to_series(name='columns')
    else:
        ret = get_sliced_value(self)
    return ret


def iterable_query_value(self):
    """Evaluate an iterable query object"""
    if self.where:
        if self.condition:
            val = self.obj.value[self.condition.value]
        elif self.where_all:
            cond_values = (c.value for c in self.conditions)
            val = self.obj.value[reduce(lambda x, y: x & y, cond_values)]
        elif self.where_any:
            cond_values = (c.value for c in self.conditions)
            val = self.obj.value[reduce(lambda x, y: x | y, cond_values)]
    else:
        val = self.obj.value
    if self.columns:
        val = val[self.columns]
    return val.reset_index(drop=True)


def condition_in_value(self):
    """Evaluate a condition-in"""
    qobj_ref_val = get_parent_of_type('IterableQuery', self).obj.value
    if isinstance(qobj_ref_val, pandas.core.frame.DataFrame):
        column = qobj_ref_val[self.column]
    else:
        assert isinstance(qobj_ref_val, pandas.core.series.Series)
        column = qobj_ref_val
    if self.parameter:
        return column.isin(self.parameter.value.tolist())
    return column.isin([p.value for p in self.params])


def condition_comparison_value(self):
    """Evaluate a condition comparison"""
    qobj_ref_val = get_parent_of_type('IterableQuery', self).obj.value
    if isinstance(qobj_ref_val, pandas.core.frame.DataFrame):
        column_left = qobj_ref_val[self.column_left] if self.column_left else None
        column_right = qobj_ref_val[self.column_right] if self.column_right else None
    else:
        assert isinstance(qobj_ref_val, pandas.core.series.Series)
        column_left = qobj_ref_val if self.column_left else None
        column_right = qobj_ref_val if self.column_right else None

    left = column_left if self.column_left else self.operand_left.value
    right = column_right if self.column_right else self.operand_right.value
    return comp_map[self.operator](left, right)


def plain_type_value(self):
    """Evaluate an object of plain type (string or boolean)"""
    if self.need_input:
        self.__value = checktype_(load_value(self.url, self.filename), self.type_)
        self.need_input = False
    return self.__value


def quantity_value(self):
    """Evaluate a quantity object"""
    if self.need_input:
        val = checktype_(load_value(self.url, self.filename), self.type_)
        self.need_input = False
        return val
    magnitude = numpy.nan if self.inp_value.value is None else self.inp_value.value
    return typemap['Quantity'](magnitude, self.inp_units)


def range_value(self):
    """Evaluate the range builtin function"""
    unit = self.start.value.units
    data = numpy.arange(self.start.value.magnitude,
                        self.stop.value.to(unit).magnitude,
                        self.step.value.to(unit).magnitude).tolist()
    # somewhat redundant code with series_value()
    if all(isinstance(e, int) for e in data):
        data = (typemap['Quantity'](e, unit) for e in data)
        dtype = 'object'
    else:
        assert all(isinstance(e, float) for e in data)
        dtype = pint_pandas.PintType(unit)
    name = self.parent.name if hasattr(self.parent, 'name') else None
    return typemap['Series'](data=data, name=name, dtype=dtype)


def map_value(self):
    """Evaluate the map builtin function"""
    func = self.lambda_ if self.lambda_ else self.function
    values = [p.value for p in self.params]
    dtypes = [p.type_.datatype for p in self.params]
    types = []
    for dtype in dtypes:
        if dtype is None or issubclass(dtype, (bool, str)):
            types.append(dtype)
        elif issubclass(dtype, scalar_numtype):
            types.append(DType('Quantity', (typemap['Quantity'],), {'datatype': dtype}))
        else:
            types.append(dtype)
    if not isinstance_m(func, ['ObjectImport']):
        lst_value = [subst(self, func, p, types).value for p in zip(*values)]
    else:
        lst_value = map(get_object_import(func), *values)
    name = self.parent.name if hasattr(self.parent, 'name') else None
    return typemap['Series'](name=name, data=lst_value)


def filter_value(self):
    """Evaluate the filter builtin function"""
    filter_f = self.lambda_ if self.lambda_ else self.function
    filter_d = self.parameter.value.dropna()
    if not isinstance_m(filter_f, ['ObjectImport']):
        dtype = self.parameter.type_.datatype
        if dtype is None or issubclass(dtype, (bool, str)):
            type_ = dtype
        elif issubclass(dtype, scalar_numtype):
            type_ = DType('Quantity', (typemap['Quantity'],), {'datatype': dtype})
        else:
            type_ = dtype
        lst = [p for p in filter_d if subst(self, filter_f, (p,), (type_,)).value]
    else:
        lst = filter(get_object_import(filter_f), filter_d)
    name = self.parent.name if hasattr(self.parent, 'name') else None
    return typemap['Series'](name=name, data=lst)


def reduce_value(self):
    """Evaluate the reduce builtin function"""
    func = self.lambda_ if self.lambda_ else self.function
    elements = iter(self.parameter.value)
    if not isinstance_m(func, ['ObjectImport']):
        value = next(elements)
        dtype = self.parameter.type_.datatype
        if dtype is None or issubclass(dtype, (bool, str)):
            type_ = dtype
        elif issubclass(dtype, scalar_numtype):
            type_ = DType('Quantity', (typemap['Quantity'],), {'datatype': dtype})
        else:
            type_ = dtype
        for elem in elements:
            value = subst(self, func, (value, elem), (type_, type_)).value
    else:
        value = reduce(get_object_import(func), elements)
    return value


def func_reduce_value(self, func):
    """Evaluate a python builtin reduce function (sum, all, any)"""
    if self.parameter:
        ret = func(self.parameter.value)
    else:
        ret = func(p.value for p in self.params)
    if not issubclass(type(ret), self.type_):
        ret = self.type_(ret)
    return ret


def in_value(self):
    """Evaluate membership of an object in a tuple, series or table"""
    if self.parameter:
        ret = self.element.value in self.parameter.value.values
    else:
        ret = self.element.value in (p.value for p in self.params)
    return self.type_(ret)


def amml_structure_value(self):
    """Evaluate an AMML structure"""
    if self.filename or self.url:
        suffix = pathlib.Path(self.filename).suffix
        if self.filename and suffix not in ['.yml', '.yaml', '.json']:
            return amml.AMMLStructure.from_ase_file(self.filename)
        return checktype_(load_value(self.url, self.filename), self.type_)
    return amml.AMMLStructure(self.tab.value, self.name)


def amml_calculator_value(self):
    """Evaluate an AMML calculator object"""
    params = pandas.DataFrame() if self.parameters is None else self.parameters.value
    return amml.Calculator(self.name, params, pinning=self.pinning,
                           version=self.version, task=self.task)


def amml_algorithm_value(self):
    """Evaluate an AMML algorithm object"""
    params = pandas.DataFrame() if self.parameters is None else self.parameters.value
    return amml.Algorithm(self.name, params, self.many_to_one)


def amml_property_value(self):
    """Evaluate an AMML property object"""
    return amml.Property(self.names, self.struct.value,
                         calculator=self.calc and self.calc.value,
                         algorithm=self.algo and self.algo.value,
                         constraints=[c.value for c in self.constrs])


def amml_constraint_value(self):
    """Evaluate an AMML constraint object"""
    direction = None if self.direction is None else self.direction.value
    return amml.Constraint(self.name, fixed=self.fixed.value, direction=direction)


def chem_reaction_value(self):
    """Evaluate a chemical reaction object"""
    species = [t.species.value for t in self.educts+self.products]
    coeffs = []
    for term in self.educts:
        coeffs.append(-term.coefficient)
    for term in self.products:
        coeffs.append(term.coefficient)
    terms = [{'coefficient': c, 'species': s} for c, s in zip(coeffs, species)]
    props = self.props and self.props.value
    return chemistry.ChemReaction(terms, props)


def chem_species_value(self):
    """Evaluate a chemical species object"""
    props = self.props and self.props.value
    composition = self.composition and self.composition.value
    return chemistry.ChemSpecies(self.name, composition, props=props)


def add_value_properties(metamodel):
    """Add object class properties using monkey style patching"""
    mapping_dict = {
        'Program': program_value,
        'Variable': variable_value,
        'GeneralReference': general_reference_value,
        'Factor': factor_value,
        'Term': term_value,
        'Expression': expression_value,
        'Power': power_value,
        'Operand': operand_value,
        'BooleanOperand': operand_value,
        'And': partial(binary_operation_value, operator=lambda x, y: x and y),
        'Or': partial(binary_operation_value, operator=lambda x, y: x or y),
        'Not': partial(not_value, operator=not_),
        'PrintParameter': print_parameter_value,
        'Type': type_value,
        'Real': lambda x: x.parameter.value.real,
        'Imag': lambda x: x.parameter.value.imag,
        'IfFunction': if_expression_value,
        'IfExpression': if_expression_value,
        'Comparison': comparison_value,
        'ObjectImport': object_import_value,
        'FunctionCall': function_call_value,
        'Tuple': tuple_value,
        'VarTuple': variable_value,
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
        'IterableProperty': iterable_property_value,
        'IterableQuery': iterable_query_value,
        'ConditionOr': partial(binary_operation_value, operator=or_),
        'ConditionAnd': partial(binary_operation_value, operator=and_),
        'ConditionNot': partial(not_value, operator=invert),
        'ConditionComparison': condition_comparison_value,
        'ConditionIn': condition_in_value,
        'String': plain_type_value,
        'Bool': plain_type_value,
        'Quantity': quantity_value,
        'Range': range_value,
        'In': in_value,
        'Any': partial(func_reduce_value, func=any),
        'All': partial(func_reduce_value, func=all),
        'Sum': partial(func_reduce_value, func=sum),
        'Map': map_value,
        'Filter': filter_value,
        'Reduce': reduce_value,
        'AMMLStructure': amml_structure_value,
        'AMMLCalculator': amml_calculator_value,
        'AMMLAlgorithm': amml_algorithm_value,
        'AMMLProperty': amml_property_value,
        'AMMLConstraint': amml_constraint_value,
        'ChemReaction': chem_reaction_value,
        'ChemSpecies': chem_species_value
    }
    for key, func in mapping_dict.items():
        metamodel[key].value = cached_property(textxerror_wrap(checktype(func)))
        metamodel[key].value.__set_name__(metamodel[key], 'value')
    metamodel['Print'].value = print_value
