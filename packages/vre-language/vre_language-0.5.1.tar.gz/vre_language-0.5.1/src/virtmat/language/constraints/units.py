"""
check the units of specific quantities
"""
from virtmat.language.utilities.errors import textxerror_wrap, InvalidUnitError
from virtmat.language.utilities.serializable import ureg


@textxerror_wrap
def check_number_literal_units(obj, qname, unit):
    """check for invalid units in a number literal"""
    if obj.need_input:
        raise ValueError(f'{qname} must be a literal')
    test = ureg.Quantity(0, obj.inp_units)
    if str(test.to_base_units().units) != unit:
        raise InvalidUnitError(f'invalid unit of {qname}: {obj.inp_units}')


@textxerror_wrap
def check_units(obj, dimensionality):
    """check dimensionality of an object that has inp_units attribute"""
    assert hasattr(obj, 'inp_units')
    if not ureg.Quantity(1., obj.inp_units).check(dimensionality):
        msg = f'object must have dimensionality of {dimensionality}'
        raise InvalidUnitError(msg)
