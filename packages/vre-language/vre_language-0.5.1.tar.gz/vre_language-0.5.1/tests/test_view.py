"""
tests for the view statements
"""
import pytest


@pytest.fixture(name='model_kwargs_no_display')
def fixture_kwargs(model_kwargs):
    """deactivate display graphics (such as matplotlib) on the screen"""
    model_kwargs['display_graphics'] = False
    return model_kwargs


def test_long_form_data(meta_model, model_kwargs_no_display):
    """test plotting long-form data"""
    inp = ("tab = ("
           "(number: 1, 2, 3, 4, 1, 2, 3, 4) [meter],"
           "(type_: 'square', 'square', 'square', 'square', "
           "'cube', 'cube', 'cube', 'cube'),"
           "(value: 1, 4, 9, 16, 1, 8, 27, 64),"
           "(time: 0., 1., 2., 3., 4., 5., 6., 7.) [hour]);"
           "view lineplot (tab, 'number', 'value');"
           "view scatterplot (tab, 'number', 'value')")
    meta_model.model_from_str(inp, **model_kwargs_no_display)


def test_long_form_data_with_custom_units(meta_model, model_kwargs_no_display):
    """test plotting long-form data with custom units"""
    inp = ("tab = ("
           "(number: 1, 2, 3, 4, 1, 2, 3, 4) [meter],"
           "(type_: 'square', 'square', 'square', 'square', "
           "'cube', 'cube', 'cube', 'cube'),"
           "(value: 1, 4, 9, 16, 1, 8, 27, 64),"
           "(time: 0., 1., 2., 3., 4., 5., 6., 7.) [hour]);"
           "units = (units: 'cm', '', '', 'hour');"
           "view lineplot (tab, 'number', 'value', units);"
           "view lineplot (tab, 'number', 'time', (units: 'inch', null, '', 'second'))")
    meta_model.model_from_str(inp, **model_kwargs_no_display)


def test_long_form_data_with_wrong_units(meta_model, model_kwargs_no_display, capsys):
    """test plotting long-form data with wrong custom units"""
    inp = ("tab = ("
           "(number: 1, 2, 3, 4, 1, 2, 3, 4) [meter],"
           "(type_: 'square', 'square', 'square', 'square', "
           "'cube', 'cube', 'cube', 'cube'),"
           "(value: 1, 4, 9, 16, 1, 8, 27, 64),"
           "(time: 0., 1., 2., 3., 4., 5., 6., 7.) [hour]);"
           "units_wrong = (blah: 'cm', '', '', 'hour');"
           "view lineplot (tab, 'number', 'value', units_wrong)")
    meta_model.model_from_str(inp, **model_kwargs_no_display)
    std_err = capsys.readouterr().err
    assert 'Type error: None:' in std_err
    assert 'parameter must be series with name "units"' in std_err


def test_wide_form_data(meta_model, model_kwargs_no_display):
    """test plotting wide-form data"""
    inp = ("val_ser = (values: [1, 4, 9, 16], [1, 8, 27, 64]);"
           "val_arr = val_ser:array; ind = (number: 1, 2, 3, 4) [meter];"
           "ind_arr = ind:array; columns = (columns: 'square', 'cube');"
           "columns_u = ('square [m**2]', 'cube [m**3]');"
           "view lineplot (val_arr, ind_arr [km], columns_u);"
           "view lineplot (val_ser, ind [cm], columns);"
           "view lineplot (val_arr, ind [km], columns);"
           "view lineplot (val_ser, ind_arr [cm], columns_u)")
    meta_model.model_from_str(inp, **model_kwargs_no_display)


def test_simple_xy_data(meta_model, model_kwargs_no_display):
    """test plotting simple xy-data"""
    inp = ("ind = (number: 1, 2, 3, 4) [meter]; sqr = (square: 1, 4, 9, 16);"
           "view lineplot (sqr, ind [mm]);"
           "view lineplot (sqr:array, ind:array);"
           "view lineplot (sqr, ind:array);"
           "view lineplot (sqr:array, ind)")
    meta_model.model_from_str(inp, **model_kwargs_no_display)


def test_simple_xy_data_not_computed(meta_model, model_kwargs_no_display, capsys):
    """test plotting data that are not computed"""
    model_kwargs_no_display['autorun'] = False
    inp = ("ind = (number: 1, 2, 3, 4) [meter]; sqr = (square: 1, 4, 9, 16);"
           "view lineplot (sqr, ind [mm])")
    meta_model.model_from_str(inp, **model_kwargs_no_display)
    std_err = capsys.readouterr().err
    if model_kwargs_no_display.get('workflow_mode'):
        assert 'Warning:' in std_err
        assert 'parameter value is not computed yet' in std_err
