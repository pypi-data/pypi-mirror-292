"""
tests of i/o operations
"""
import os
import pytest
import yaml
import numpy
from textx import get_children_of_type
from textx.exceptions import TextXError
from virtmat.language.utilities.serializable import series2dict
from virtmat.language.utilities.serializable import FWDataFrame, FWNumArray
from virtmat.language.utilities.errors import RuntimeTypeError


def tuple2list(obj):
    """convert arbitrarily nested tuples to lists in an arbitrary object"""
    if isinstance(obj, (tuple, list)):
        new_obj = [tuple2list(elem) for elem in obj]
    elif isinstance(obj, dict):
        new_obj = {key: tuple2list(val) for key, val in obj.items()}
    else:
        new_obj = obj
    return new_obj


STRING_DATA = 'domain specific languages help a lot!'
BOOL_DATA = True
NUMBER_DATA = {'_fw_name': '{{virtmat.language.utilities.serializable.FWQuantity}}',
               'data': (3.1415, (('radian', 1),))}
SERIES_DATA = {'_fw_name': '{{virtmat.language.utilities.serializable.FWSeries}}',
               'data': [1.0, 2.0, 3.0], 'name': 'temperature', 'units': 'kelvin'}
TABLE_DATA = {'_fw_name': '{{virtmat.language.utilities.serializable.FWDataFrame}}',
              'data': [{'_fw_name': '{{virtmat.language.utilities.serializable.FWSeries}}',
                        'name': 'pressure', 'data': [100.0, 200.0, 300.0], 'units': 'bar'},
                       {'_fw_name': '{{virtmat.language.utilities.serializable.FWSeries}}',
                        'name': 'temperature', 'data': [1.0, 2.0, 3.0], 'units': 'kelvin'}]}
ARRAY_DATA = {'_fw_name': '{{virtmat.language.utilities.serializable.FWNumArray}}',
              'data': [[0.59656566, 0.59656566, -1.3e-13], [['bohr', 1],
                       ['elementary_charge', 1]]], 'dtype': 'float64'}
S_ARRAY_DATA = {'_fw_name': '{{virtmat.language.utilities.serializable.FWSeries}}',
                'data': [ARRAY_DATA], 'name': 'dipole'}


@pytest.fixture(name='string_input_file')
def string_input_fixture(tmp_path):
    """prepare an input source with a string"""
    source = os.path.join(tmp_path, 'string_in.yaml')
    with open(source, 'w', encoding='utf-8') as ifile:
        yaml.safe_dump(STRING_DATA, ifile)
    return source


@pytest.fixture(name='bool_input_file')
def bool_input_fixture(tmp_path):
    """prepare an input source with a bool"""
    source = os.path.join(tmp_path, 'bool_in.yaml')
    with open(source, 'w', encoding='utf-8') as ifile:
        yaml.safe_dump(BOOL_DATA, ifile)
    return source


@pytest.fixture(name='number_input_file')
def number_input_fixture(tmp_path):
    """prepare an input source with a number"""
    source = os.path.join(tmp_path, 'number_in.yaml')
    with open(source, 'w', encoding='utf-8') as ifile:
        yaml.safe_dump(NUMBER_DATA, ifile)
    return source


@pytest.fixture(name='series_input_file')
def series_input_fixture(tmp_path):
    """prepare an input source with a series"""
    source = os.path.join(tmp_path, 'series_in.yaml')
    with open(source, 'w', encoding='utf-8') as ifile:
        yaml.safe_dump(SERIES_DATA, ifile)
    return source


@pytest.fixture(name='table_input_file')
def table_input_fixture(tmp_path):
    """prepare an input source with a table"""
    source = os.path.join(tmp_path, 'table_in.yaml')
    with open(source, 'w', encoding='utf-8') as ifile:
        yaml.safe_dump(TABLE_DATA, ifile)
    return source


@pytest.fixture(name='array_input_file')
def array_input_fixture(tmp_path):
    """prepare an input source with an array"""
    source = os.path.join(tmp_path, 'array_in.yaml')
    with open(source, 'w', encoding='utf-8') as ifile:
        yaml.safe_dump(ARRAY_DATA, ifile)
    return source


@pytest.fixture(name='s_array_input_file')
def series_array_input_fixture(tmp_path):
    """prepare an input source with a series of arrays"""
    source = os.path.join(tmp_path, 'sarray_in.yaml')
    with open(source, 'w', encoding='utf-8') as ifile:
        yaml.safe_dump(S_ARRAY_DATA, ifile)
    return source


@pytest.fixture(name='output_file')
def output_file_fixture(tmp_path):
    """prepare an output target"""
    return os.path.join(tmp_path, 'output.yaml')


def test_string_from_file(meta_model, string_input_file, model_kwargs):
    """test reading a string from file"""
    prog_str = "a = String from file \'" + string_input_file + "\'"
    prog = meta_model.model_from_str(prog_str, **model_kwargs)
    var_list = get_children_of_type('Variable', prog)
    assert next(v for v in var_list if v.name == 'a').value == STRING_DATA


def test_string_from_file_wrong(meta_model, number_input_file, model_kwargs):
    """test reading a string from file with input of wrong type"""
    prog_str = "a = String from file \'" + number_input_file + "\'"
    prog = meta_model.model_from_str(prog_str, **model_kwargs)
    var_list = get_children_of_type('Variable', prog)
    match_str = "must be <class 'str'>"
    with pytest.raises(TextXError, match=match_str) as err_info:
        _ = next(v for v in var_list if v.name == 'a').value
    assert isinstance(err_info.value.__cause__, RuntimeTypeError)


def test_bool_from_file(meta_model, bool_input_file, model_kwargs):
    """test reading a boolean from file"""
    prog_str = "a = Bool from file \'" + bool_input_file + "\'"
    prog = meta_model.model_from_str(prog_str, **model_kwargs)
    var_list = get_children_of_type('Variable', prog)
    assert next(v for v in var_list if v.name == 'a').value == BOOL_DATA


def test_bool_from_file_wrong(meta_model, string_input_file, model_kwargs):
    """test reading a boolean from file with input of wrong type"""
    prog_str = "a = Bool from file \'" + string_input_file + "\'"
    prog = meta_model.model_from_str(prog_str, **model_kwargs)
    var_list = get_children_of_type('Variable', prog)
    match_str = "must be <class 'bool'>"
    with pytest.raises(TextXError, match=match_str) as err_info:
        _ = next(v for v in var_list if v.name == 'a').value
    assert isinstance(err_info.value.__cause__, RuntimeTypeError)


def test_number_from_file(meta_model, number_input_file, model_kwargs):
    """test reading a quantity from file"""
    prog_str = "a = Quantity from file \'" + number_input_file + "\'"
    prog = meta_model.model_from_str(prog_str, **model_kwargs)
    var_list = get_children_of_type('Variable', prog)
    a_val = next(v for v in var_list if v.name == 'a').value
    assert a_val.to_tuple() == NUMBER_DATA['data']


def test_number_from_file_wrong(meta_model, bool_input_file, model_kwargs):
    """test reading a quantity from file with input of wrong type"""
    prog_str = "a = Quantity from file \'" + bool_input_file + "\'"
    prog = meta_model.model_from_str(prog_str, **model_kwargs)
    var_list = get_children_of_type('Variable', prog)
    match_str = "type must be <class 'pint.Quantity'> but is <class 'bool'>"
    with pytest.raises(TextXError, match=match_str) as err_info:
        _ = next(v for v in var_list if v.name == 'a').value
    assert isinstance(err_info.value.__cause__, RuntimeTypeError)


def test_number_from_file_wrong_schema(meta_model, series_input_file, model_kwargs):
    """test reading a quantity from file with input of wrong schema"""
    prog_str = "a = Quantity from file \'" + series_input_file + "\'"
    prog = meta_model.model_from_str(prog_str, **model_kwargs)
    var_list = get_children_of_type('Variable', prog)
    msg = "type must be <class 'pint.(quantity.build_quantity_class.<locals>.)?Quantity'>"
    with pytest.raises(TextXError, match=msg) as err_info:
        _ = next(v for v in var_list if v.name == 'a').value
    assert isinstance(err_info.value.__cause__, RuntimeTypeError)


def test_series_from_file(meta_model, series_input_file, model_kwargs):
    """test reading a series from file"""
    prog_str = "a = Series from file \'" + series_input_file + "\'"
    prog = meta_model.model_from_str(prog_str, **model_kwargs)
    var_list = get_children_of_type('Variable', prog)
    a_val = next(v for v in var_list if v.name == 'a').value
    assert series2dict(a_val)['data'] == SERIES_DATA['data']
    assert series2dict(a_val)['name'] == SERIES_DATA['name']
    assert series2dict(a_val)['units'] == SERIES_DATA['units']


def test_series_from_file_wrong(meta_model, string_input_file, model_kwargs):
    """test reading a series from file with input of wrong type"""
    prog_str = "a = Series from file \'" + string_input_file + "\'"
    prog = meta_model.model_from_str(prog_str, **model_kwargs)
    var_list = get_children_of_type('Variable', prog)
    match_str = "type must be <class 'pandas.core.series.Series'> but is <class 'str'>"
    with pytest.raises(TextXError, match=match_str) as err_info:
        _ = next(v for v in var_list if v.name == 'a').value
    assert isinstance(err_info.value.__cause__, RuntimeTypeError)


def test_series_from_file_wrong_schema(meta_model, number_input_file, model_kwargs):
    """test reading a series from file with input of wrong schema"""
    prog_str = "a = Series from file \'" + number_input_file + "\'"
    prog = meta_model.model_from_str(prog_str, **model_kwargs)
    var_list = get_children_of_type('Variable', prog)
    msg = "type must be <class 'pandas.core.series.Series'>"
    with pytest.raises(TextXError, match=msg) as err_info:
        _ = next(v for v in var_list if v.name == 'a').value
    assert isinstance(err_info.value.__cause__, RuntimeTypeError)


def test_table_from_file(meta_model, table_input_file, model_kwargs):
    """test reading a table from file"""
    prog_str = "a = Table from file \'" + table_input_file + "\'"
    prog = meta_model.model_from_str(prog_str, **model_kwargs)
    var_list = get_children_of_type('Variable', prog)
    data_frame = next(v for v in var_list if v.name == 'a').value
    assert data_frame.equals(FWDataFrame.from_dict(TABLE_DATA))


def test_table_from_file_wrong(meta_model, bool_input_file, model_kwargs):
    """test reading a table from file with input of wrong type"""
    prog_str = "a = Table from file \'" + bool_input_file + "\'"
    prog = meta_model.model_from_str(prog_str, **model_kwargs)
    var_list = get_children_of_type('Variable', prog)
    match_str = "type must be <class 'pandas.core.frame.DataFrame'> but is <class 'bool'>"
    with pytest.raises(TextXError, match=match_str) as err_info:
        _ = next(v for v in var_list if v.name == 'a').value
    assert isinstance(err_info.value.__cause__, RuntimeTypeError)


def test_table_from_file_wrong_schema(meta_model, series_input_file, model_kwargs):
    """test reading a table from file with input of wrong schema"""
    prog_str = "a = Table from file \'" + series_input_file + "\'"
    prog = meta_model.model_from_str(prog_str, **model_kwargs)
    var_list = get_children_of_type('Variable', prog)
    msg = "type must be <class 'pandas.core.frame.DataFrame'>"
    with pytest.raises(TextXError, match=msg) as err_info:
        _ = next(v for v in var_list if v.name == 'a').value
    assert isinstance(err_info.value.__cause__, RuntimeTypeError)


def test_float_array_from_file(meta_model, array_input_file, model_kwargs):
    """test reading a float array from file"""
    prog_str = "a = FloatArray from file \'" + array_input_file + "\'"
    prog = meta_model.model_from_str(prog_str, **model_kwargs)
    var_list = get_children_of_type('Variable', prog)
    array = next(v for v in var_list if v.name == 'a').value
    assert numpy.allclose(array, FWNumArray.from_dict(ARRAY_DATA))


def test_float_array_from_file_wrong(meta_model, series_input_file, model_kwargs):
    """test reading a float array from a wrong file"""
    prog_str = "a = FloatArray from file \'" + series_input_file + "\'"
    prog = meta_model.model_from_str(prog_str, **model_kwargs)
    var_list = get_children_of_type('Variable', prog)
    msg = "type must be <class 'pint.(quantity.build_quantity_class.<locals>.)?Quantity'>"
    with pytest.raises(TextXError, match=msg) as err_info:
        _ = next(v for v in var_list if v.name == 'a').value
    assert isinstance(err_info.value.__cause__, RuntimeTypeError)


def test_series_float_array_from_file(meta_model, s_array_input_file, model_kwargs):
    """test reading a series of float arrays from file"""
    prog_str = "a = Series from file \'" + s_array_input_file + "\'"
    prog = meta_model.model_from_str(prog_str, **model_kwargs)
    var_list = get_children_of_type('Variable', prog)
    array = next(v for v in var_list if v.name == 'a').value[0]
    assert numpy.allclose(array, FWNumArray.from_dict(ARRAY_DATA))


def test_string_to_file(meta_model, output_file, model_kwargs):
    """test writing a string to file"""
    string_repr = "\'" + STRING_DATA + "\'"
    prog_str = "a = " + string_repr + "; a to file \'" + output_file + "\'"
    meta_model.model_from_str(prog_str, **model_kwargs)
    with open(output_file, 'r', encoding='utf-8') as ofile:
        assert yaml.safe_load(ofile) == STRING_DATA


def test_bool_to_file(meta_model, output_file, model_kwargs):
    """test writing a bool to file"""
    bool_repr = "true"
    prog_str = "a =  " + bool_repr + "; a to file \'" + output_file + "\'"
    meta_model.model_from_str(prog_str, **model_kwargs)
    with open(output_file, 'r', encoding='utf-8') as ofile:
        assert yaml.safe_load(ofile) == BOOL_DATA


def test_number_to_file(meta_model, output_file, model_kwargs):
    """test writing a number to file"""
    number_repr = "3.1415 [radian]"
    prog_str = "a = " + number_repr + "; a to file \'" + output_file + "\'"
    meta_model.model_from_str(prog_str, **model_kwargs)
    with open(output_file, 'r', encoding='utf-8') as ofile:
        loaded_data = yaml.safe_load(ofile)
    assert loaded_data['data'] == tuple2list(NUMBER_DATA['data'])


def test_series_to_file(meta_model, output_file, model_kwargs):
    """test writing a series to file"""
    series_repr = "(temperature: 1.0, 2.0, 3.0) [kelvin]"
    prog_str = "a = " + series_repr + "; a to file \'" + output_file + "\'"
    meta_model.model_from_str(prog_str, **model_kwargs)
    with open(output_file, 'r', encoding='utf-8') as ofile:
        loaded_data = yaml.safe_load(ofile)
    assert loaded_data['name'] == SERIES_DATA['name']
    assert loaded_data['data'] == SERIES_DATA['data']
    assert loaded_data['units'] == SERIES_DATA['units']


def test_table_to_file(meta_model, output_file, model_kwargs):
    """test writing a table to file"""
    table_repr = ("((pressure: 100.0, 200.0, 300.0) [bar], "
                  "(temperature: 1.0, 2.0, 3.0) [kelvin])")
    prog_str = "a = " + table_repr + "; a to file \'" + output_file + "\'"
    meta_model.model_from_str(prog_str, **model_kwargs)
    with open(output_file, 'r', encoding='utf-8') as ofile:
        loaded_data = yaml.safe_load(ofile)
    assert loaded_data['_fw_name'] == TABLE_DATA['_fw_name']
    for ind in (0, 1):
        assert loaded_data['data'][ind]['_fw_name'] == TABLE_DATA['data'][ind]['_fw_name']
        assert loaded_data['data'][ind]['data'] == TABLE_DATA['data'][ind]['data']
        assert loaded_data['data'][ind]['name'] == TABLE_DATA['data'][ind]['name']
        assert loaded_data['data'][ind]['units'] == TABLE_DATA['data'][ind]['units']


def test_float_array_to_file(meta_model, output_file, model_kwargs):
    """test writing a float array to file"""
    array_repr = '[0.59656566, 0.59656566, -1.3e-13] [bohr*elementary_charge]'
    prog_str = "a = " + array_repr + "; a to file \'" + output_file + "\'"
    meta_model.model_from_str(prog_str, **model_kwargs)
    with open(output_file, 'r', encoding='utf-8') as ofile:
        loaded_data = yaml.safe_load(ofile)
    assert loaded_data['_fw_name'] == ARRAY_DATA['_fw_name']


def test_series_float_array_to_file(meta_model, output_file, model_kwargs):
    """test writing a series with a float array to file"""
    series_repr = '(dipole: [0.59656566, 0.59656566, -1.3e-13]) [bohr*elementary_charge]'
    prog_str = "a = " + series_repr + "; a to file \'" + output_file + "\'"
    meta_model.model_from_str(prog_str, **model_kwargs)
    with open(output_file, 'r', encoding='utf-8') as ofile:
        loaded_data = yaml.safe_load(ofile)
    assert loaded_data['_fw_name'] == S_ARRAY_DATA['_fw_name']


def test_print_number_units_nounits(meta_model, model_kwargs):
    """test printing numbers with units and no units"""
    prog_str = 'print(3.1 [meter], -1.0)'
    prog = meta_model.model_from_str(prog_str, **model_kwargs)
    assert prog.value == '3.1 [meter] -1.0'


def test_print_bool(meta_model, model_kwargs):
    """test printing booleans"""
    prog_str = 'print(true, false)'
    prog = meta_model.model_from_str(prog_str, **model_kwargs)
    assert prog.value == 'true false'


def test_print_string(meta_model, model_kwargs):
    """test printing strings"""
    prog_str = 'print("Abc")'
    prog = meta_model.model_from_str(prog_str, **model_kwargs)
    assert prog.value == '\'Abc\''


def test_print_series(meta_model, model_kwargs):
    """test printing series"""
    prog_str = ('a = (integers: 1, 2) [meter];'
                'b = (floats: 1., -1.) [cm];'
                'c = (booleans: true, false);'
                'd = (strings: "a", "b");'
                'print(a, b, c, d)')
    prog = meta_model.model_from_str(prog_str, **model_kwargs)
    assert prog.value == ('(integers: 1, 2) [meter] (floats: 1.0, -1.0) [centimeter] '
                          '(booleans: true, false) (strings: \'a\', \'b\')')


def test_print_table(meta_model, model_kwargs):
    """test printing a table"""
    table_inp = ('((pressure: 100.0, 200.0, 300.0) [bar], '
                 '(temperature: 1.0, 2.0, 3.0) [kelvin], '
                 '(corrected: true, true, false), '
                 '(source: \'url\', \'file\', \'interactive\'))')
    prog_str = 'a = ' + table_inp + '; print(a)'
    prog = meta_model.model_from_str(prog_str, **model_kwargs)
    assert prog.value == table_inp


def test_print_tuple(meta_model, model_kwargs):
    """test printing a tuple"""
    tuple_inp = '(1, 2.0 [centimeter], true, \'string\', (numbs: 1, 3))'
    prog_str = 'a = ' + tuple_inp + '; print(a)'
    prog = meta_model.model_from_str(prog_str, **model_kwargs)
    assert prog.value == tuple_inp


def test_print_bool_array(meta_model, model_kwargs):
    """test printing a bool array"""
    array_inp = '[true, true, false]'
    prog_str = 'a = ' + array_inp + '; print(a)'
    prog = meta_model.model_from_str(prog_str, **model_kwargs)
    assert prog.value == array_inp


def test_print_str_array(meta_model, model_kwargs):
    """test printing a str array"""
    array_inp = "['a', 'abc']"
    prog_str = 'a = ' + array_inp + '; print(a)'
    prog = meta_model.model_from_str(prog_str, **model_kwargs)
    assert prog.value == array_inp


def test_print_int_array(meta_model, model_kwargs):
    """test printing an int array"""
    array_inp = '[[1, 0, 0], [0, 1, 0]]'
    prog_str = 'a = ' + array_inp + '; print(a)'
    prog = meta_model.model_from_str(prog_str, **model_kwargs)
    assert prog.value == array_inp


def test_print_float_array(meta_model, model_kwargs):
    """test printing a float array"""
    array_inp = '[[1.0, 0.0, 0.0], [1.0, 1.0, 0.0]] [angstrom]'
    prog_str = 'a = ' + array_inp + '; print(a)'
    prog = meta_model.model_from_str(prog_str, **model_kwargs)
    assert prog.value == array_inp


def test_print_series_float_arrays(meta_model, model_kwargs):
    """test printing a series of float arrays"""
    series_inp = '(positions: [[1.0, 0.0, 0.0], [1.0, 1.0, 0.0]]) [angstrom]'
    prog_str = 'a = ' + series_inp + '; print(a)'
    prog = meta_model.model_from_str(prog_str, **model_kwargs)
    assert prog.value == series_inp
