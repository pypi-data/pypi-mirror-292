"""module for data visualization"""
import numpy
import pandas
import seaborn
from matplotlib import pyplot
from textx import get_children_of_type, textx_isinstance
from ase import visualize
from virtmat.language.utilities.types import is_array_type, is_array, is_numeric, NC
from virtmat.language.utilities.errors import RuntimeTypeError, RuntimeValueError
from virtmat.language.utilities.errors import raise_exception, error_handler
from virtmat.language.utilities.warnings import TextSUserWarning
from virtmat.language.utilities.units import get_units, get_df_units
from virtmat.language.utilities.units import convert_df_units, strip_units, ureg
from virtmat.language.interpreter.instant_executor import get_nested_array
from virtmat.language.interpreter.workflow_executor import get_par_value


def display_seaborn(obj):
    """Display numerical data on xy-plots using the seaborn package

      Args:
          obj (view object: instance of metamodel class View)

      The types of the values of obj.params attribute:
       * parameters for long-form data:
         tab (pandas.DataFrame): table with the data (dataframe index not used)
         x_name (str): the name of the column to use as x axis
         y_name (str): the name of the column to use as y axis
         units (series): string series owith name 'units' and of length the
           number of columns in tab

       * parameters for wide-form data:
         values: series of 1D arrays or a 2D array of scalar type
           dim(values) must be either (len(index), len(columns))
                                   or (len(columns), len(index))
         index: series or 1D array of scalar type
         columns: series, 1D array or tuple of hashable types

       * parameters for simple xy data:
         values: series or 1D array of scalar type
         index: series or 1D array of scalar type

      Raises:
          RuntimeTypeError: if the types of the parameters are incorrect

    """
    sbfunc = getattr(seaborn, obj.mode)
    if issubclass(obj.params[0].type_, pandas.DataFrame):
        tab = obj.params[0].value
        x_name = obj.params[1].value
        y_name = obj.params[2].value
        try:
            assert isinstance(tab, pandas.DataFrame)
            assert isinstance(x_name, str)
            assert isinstance(y_name, str)
        except AssertionError as err:
            raise_exception(obj, RuntimeTypeError, str(err))
        if x_name not in tab.columns:
            msg = f'could not find x-axis data "{x_name}" in table'
            raise_exception(obj.params[1], RuntimeValueError, msg)
        if y_name not in tab.columns:
            msg = f'could not find y-axis data "{y_name}" in table'
            raise_exception(obj.params[2], RuntimeValueError, msg)
        if len(obj.params) > 3:
            units = obj.params[3].value
            if not isinstance(units, pandas.Series) or units.name != 'units':
                msg = 'parameter must be series with name "units"'
                raise_exception(obj.params[3], RuntimeTypeError, msg)
            if len(units) != len(tab.columns):
                msg = f'length of units series must be {len(tab.columns)}'
                raise_exception(obj.params[3], RuntimeValueError, msg)
            tab = convert_df_units(tab, units)
        units = get_df_units(tab)
        _, axes = pyplot.subplots()
        x_units = units[tab.columns.get_loc(x_name)]
        y_units = units[tab.columns.get_loc(y_name)]
        axes.set_xlabel(f'{x_name} [{x_units}]')
        axes.set_ylabel(f'{y_name} [{y_units}]')
        # axes.xaxis.set_units(x_units) #  smarter but does not work
        # axes.yaxis.set_units(y_units) #  smarter but does not work
        _ = sbfunc(tab.map(strip_units), x=x_name, y=y_name, ax=axes)
    elif (issubclass(obj.params[0].type_, pandas.Series) or
          is_array_type(obj.params[0].type_)):
        values = obj.params[0].value
        index = obj.params[1].value
        x_units = get_units(index)
        y_units = get_units(values)

        if len(obj.params) > 2:
            try:
                columns = obj.params[2].value
                if isinstance(columns, (numpy.ndarray, pandas.Series)):
                    assert len(columns.shape) == 1
                else:
                    assert isinstance(columns, (tuple, list, set))
                    columns = pandas.Series(columns)

                if isinstance(values, pandas.Series):
                    y_name = values.name
                    values = get_nested_array(values.values)
                else:
                    assert is_array(values)
                    y_name = ''

                if isinstance(index, pandas.Series):
                    x_name = index.name
                    index = index.map(strip_units)
                    if len(index) == 1 and is_array(index[0]):
                        index = index[0]
                    else:
                        index = index.values
                else:
                    assert isinstance(index, (numpy.ndarray, ureg.Quantity))
                    if isinstance(index, ureg.Quantity):
                        assert isinstance(index.magnitude, numpy.ndarray)
                    if len(index.shape) > 1:
                        assert len(index.shape) == 2
                        assert index.shape[0] == 1
                        index = index[0]
                    x_name = ''

                if columns.shape[0] != values.shape[1]:
                    assert index.shape[0] == values.shape[1]
                    assert columns.shape[0] == values.shape[0]
                    values = values.transpose()
                else:
                    assert index.shape[0] == values.shape[0]
                    assert columns.shape[0] == values.shape[1]
            except AssertionError as err:
                raise_exception(obj, RuntimeTypeError, str(err))

            if is_numeric(columns):
                columns = [f'{c.magnitude} [{c.units}]' for c in columns]

            df = pandas.DataFrame(values, index, columns=columns)
            _, axes = pyplot.subplots()
            axes.set_xlabel(f'{x_name} [{x_units}]')
            axes.set_ylabel(f'{y_name} [{y_units}]')
            _ = sbfunc(df.map(strip_units), ax=axes)
        else:
            if is_array(index):
                index = pandas.Series(index, name='x')
            if is_array(values):
                values = pandas.Series(values, name='y')
            df = pandas.concat([index, values], axis='columns')
            _, axes = pyplot.subplots()
            axes.set_xlabel(f'{index.name} [{x_units}]')
            axes.set_ylabel(f'{values.name} [{y_units}]')
            _ = sbfunc(df.map(strip_units), x=index.name, y=values.name, ax=axes)
    else:
        types = [p.type_ for p in obj.params]
        msg = f'unknown types of view params: {types}'
        raise_exception(obj, RuntimeTypeError, msg)


def display_amml_structure(obj):
    """display an atomic structure using ASE"""
    visualize.view(obj.params[0].value.to_ase())


@error_handler
def display(self, show=True):
    """define display() method in View metamodel class"""
    if any(get_par_value(par) is NC for par in self.params):
        par = next(p for p in self.params if get_par_value(p) is NC)
        raise_exception(par, TextSUserWarning, 'parameter value is not computed yet')
    if self.mode in ('lineplot', 'scatterplot'):
        display_seaborn(self)
        if show:
            pyplot.show()
    else:
        assert self.mode == 'structure'
        display_amml_structure(self)


def add_display(metamodel):
    """add display method to the View metamodel class"""
    setattr(metamodel['View'], 'display', display)


def view_processor(model, metamodel):
    """process the view objects in model"""
    if textx_isinstance(model, metamodel['Program']):
        show = getattr(model, '_tx_model_params').get('display_graphics', True)
        for view in get_children_of_type('View', model):
            view.display(show=show)
