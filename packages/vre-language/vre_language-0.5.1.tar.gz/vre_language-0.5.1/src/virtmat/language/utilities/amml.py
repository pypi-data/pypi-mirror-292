"""Custom classes for the AMML objects"""
import os
import types
import importlib
import itertools
import uuid
import math
from dataclasses import dataclass, field
from functools import cached_property
import numpy
import pandas
import pint
import pint_pandas
import ase
import ase.constraints
from pint_pandas import PintType
from ase.io import write, jsonio
from ase.utils import IOContext
from ase.build import minimize_rotation_and_translation
from ase.geometry import wrap_positions
from ase.geometry.analysis import Analysis
from ase.calculators.calculator import get_calculator_class
from ase.calculators.singlepoint import SinglePointCalculator
from ase.io.trajectory import TrajectoryWriter, TrajectoryReader
from virtmat.language.utilities.errors import RuntimeValueError, PropertyError
from virtmat.language.utilities.errors import ConvergenceError
from virtmat.language.utilities.errors import InvalidUnitError
from virtmat.language.utilities.errors import StructureInputError
from virtmat.language.utilities.units import ureg, get_pint_series
from virtmat.language.utilities.defparam import spec, par_units
from virtmat.language.utilities.lists import list_apply, list_flatten


def get_par_units(name, par, val):
    """auxiliary function to get the units of a calculator parameter"""
    params = par_units[name]
    try:
        par_def = params[par]
    except KeyError as err:
        msg = f'parameter {par} has unknown units'
        raise InvalidUnitError(msg) from err
    if isinstance(par_def, types.FunctionType):
        return par_def(val)
    return par_def


def get_params_units(calc_name, params):
    """auxiliary function to get the units for a parameters dictionary"""
    units = {}
    for param, value in params.items():
        r_units = get_par_units(calc_name, param, value)
        if isinstance(r_units, list):
            r_units = [r(params) for r in r_units]
            r_units = next(r for r in r_units if r is not None)
        units[param] = r_units
    return units


def get_params_magnitudes(calc_params, units):
    """converts parameters to canonical units and return their magnitudes"""

    def magnitudes_from_list(unit, value):
        return list_apply(lambda x: x.to(unit).magnitude, value)

    magnitudes = {}
    for par, val in calc_params.items():
        try:
            if isinstance(val, ureg.Quantity):
                magnitudes[par] = val.to(units[par]).magnitude
            elif isinstance(val, numpy.ndarray):
                if issubclass(val.dtype.type, (numpy.bool_, numpy.str_)):
                    magnitudes[par] = val
                else:
                    assert issubclass(val.dtype.type, numpy.object_)
                    magnitudes[par] = magnitudes_from_list(units[par], val.tolist())
            else:
                types_ = (bool, numpy.bool_, str, pandas.DataFrame, AMMLObject)
                assert isinstance(val, types_) or val is None, f'{par} {val} {type(val)}'
                magnitudes[par] = val
        except pint.DimensionalityError as err:
            msg = (f'error with units of parameter \"{par}\": '
                   f'must be [{units[par]}] instead of [{val.units}]')
            raise InvalidUnitError(msg) from err
    return magnitudes


def get_structure_dataframe(atoms):
    """create a structure dataframe from an ASE Atoms object"""
    lunit = pint_pandas.PintType('angstrom')
    munit = pint_pandas.PintType('amu')
    punit = pint_pandas.PintType('( amu * eV ) ** (1/2)')

    symb = pandas.Series(atoms.get_chemical_symbols(), name='symbols')
    post = atoms.get_positions().transpose()
    posx = pandas.Series(pint_pandas.PintArray(post[0], dtype=lunit), name='x')
    posy = pandas.Series(pint_pandas.PintArray(post[1], dtype=lunit), name='y')
    posz = pandas.Series(pint_pandas.PintArray(post[2], dtype=lunit), name='z')
    momt = atoms.get_momenta().transpose()
    momx = pandas.Series(pint_pandas.PintArray(momt[0], dtype=punit), name='px')
    momy = pandas.Series(pint_pandas.PintArray(momt[1], dtype=punit), name='py')
    momz = pandas.Series(pint_pandas.PintArray(momt[2], dtype=punit), name='pz')
    tags = pandas.Series(atoms.get_tags(), name='tags')
    mass = pandas.Series(pint_pandas.PintArray(atoms.get_masses(), dtype=munit), name='masses')

    atoms_cols = [symb, posx, posy, posz, momx, momy, momz, mass, tags]
    atoms_df = pandas.concat(atoms_cols, axis=1)
    cell = ureg.Quantity(atoms.get_cell().array, 'angstrom')
    struct_cols = [{'atoms': atoms_df, 'cell': cell, 'pbc': atoms.get_pbc()}]
    return pandas.DataFrame(struct_cols)


def get_calculator_dataframe(ase_calc):
    """create a calculator dataframe from an ASE Calculator object"""
    parameters = jsonio.decode(jsonio.encode(ase_calc.parameters))
    units = get_params_units(ase_calc.name.lower(), parameters)
    calc_params = {}
    for par, val in parameters.items():
        if isinstance(val, (bool, str)) or val is None:
            calc_params[par] = val
        elif isinstance(val, (int, float)):
            calc_params[par] = ureg.Quantity(val, units[par])
        elif isinstance(val, (tuple, list)):
            if all(isinstance(v, (bool, str)) for v in list_flatten(val)):
                calc_params[par] = numpy.array(val)
            else:
                assert all(isinstance(v, (int, float)) for v in list_flatten(val))
                assert units[par] is not None
                calc_params[par] = ureg.Quantity(numpy.array(val), units[par])
        elif isinstance(val, numpy.ndarray):
            if numpy.issubdtype(val.dtype, numpy.number):
                assert units[par] is not None
                calc_params[par] = ureg.Quantity(val, units[par])
            else:
                npdtypes = (numpy.bool_, numpy.str_)
                assert any(numpy.issubdtype(val.dtype, t) for t in npdtypes)
                assert units[par] is None
                calc_params[par] = val
        else:
            raise TypeError('unknown type in calculator parameters')
    return pandas.DataFrame([calc_params])


def merge_structures(structs):
    """create one AMML structure from an iterable of AMML structures"""
    struct_df = pandas.concat([s.tab for s in structs], ignore_index=True)
    return AMMLStructure(struct_df, structs[0].name)


def merge_calculators(calcs):
    """create one AMML calculator from an iterable of AMML calculators"""
    calc_df = pandas.concat([c.parameters for c in calcs], ignore_index=True)
    calc_name = calcs[0].name
    calc_pinning = calcs[0].pinning
    calc_version = calcs[0].version
    return Calculator(calc_name, calc_df, calc_pinning, calc_version)


def merge_algorithms(algos):
    """create one AMML algorithm from an iterable of AMML algorithms"""
    algo_df = pandas.concat([a.parameters for a in algos], ignore_index=True)
    algo_name = algos[0].name
    algo_mt1 = algos[0].many_to_one
    return Algorithm(algo_name, algo_df, algo_mt1)


def tm_dipole_handler(lst):
    """handler function for the electric dipole moment"""
    res = []
    for dct in lst:
        magnitude = dct['absolute value']['value']
        units = dct['absolute value']['units'].lower()
        assert units == 'debye'
        ref = ureg.Quantity(magnitude, units)
        assert dct['vector']['units'] == 'a.u.'
        vec = ureg.Quantity(dct['vector']['array'], EC_BOHR)
        test = pint.Quantity(numpy.linalg.norm(vec.to('D').magnitude), vec.to('D').units)
        assert math.isclose(test.magnitude, ref.magnitude, rel_tol=0.001)
        res.append(vec)
    return pandas.Series(res)


def vasp_vibrational_energies_handler(calc_iter):
    """retrieve vibrational energies from normal modes"""
    dtype = pint_pandas.PintType('eV')
    data = []
    for calc in calc_iter:
        vib_ene_real = calc.read_vib_freq()[0]  # returns in meV
        vib_ene_real = numpy.array(vib_ene_real)*1.0e-3
        data.append(pandas.Series(vib_ene_real, name='vibrational_energies', dtype=dtype))
    return pandas.Series(data)


def vasp_energy_minimum_handler(calc_iter):
    """determine an energy minimum from normal modes"""
    data = []
    for calc in calc_iter:
        data.append(len(calc.read_vib_freq()[1]) == 0)
    return pandas.Series(data)


def vasp_transition_state_handler(calc_iter):
    """determine a transition state from normal modes"""
    data = []
    for calc in calc_iter:
        data.append(len(calc.read_vib_freq()[1]) == 1)
    return pandas.Series(data)


def tm_vibrational_energies_handler(vibspec_iter):
    """retrieve vibrational energies from normal modes"""
    dtype = pint_pandas.PintType('eV')
    data = []
    for vibspec in vibspec_iter:
        vib_ene = []
        for eigenvalue in vibspec:
            if eigenvalue['irreducible representation']:
                assert eigenvalue['frequency']['units'] == 'cm^-1'
                fact = ase.units.invcm
                if eigenvalue['frequency']['value'] > 0.0:
                    vib_ene.append(eigenvalue['frequency']['value']*fact)
        data.append(pandas.Series(vib_ene, name='vibrational_energies', dtype=dtype))
    return pandas.Series(data)


def tm_energy_minimum_handler(vibspec_iter):
    """determine an energy minimum from normal modes"""
    data = []
    for vibspec in vibspec_iter:
        real = True
        for eigenvalue in vibspec:
            if eigenvalue['irreducible representation']:
                if eigenvalue['frequency']['value'] < 0.0:
                    real = False
                    break
        data.append(real)
    return pandas.Series(data)


def tm_transition_state_handler(vibspec_iter):
    """determine a transition state from normal modes"""
    data = []
    for vibspec in vibspec_iter:
        im = []
        for eigenvalue in vibspec:
            if eigenvalue['irreducible representation']:
                im.append(eigenvalue['frequency']['value'] < 0.0)
        data.append(sum(im) == 1)
    return pandas.Series(data)


EC_ANG = 'elementary_charge * angstrom'
EC_BOHR = 'elementary_charge * bohr'
EV_PER_ANG = 'eV / angstrom'

ase_p_df = pandas.DataFrame(
    [
        {
         'calc_name': 'generic',
         'prop_name': 'energy',
         'internal_name': 'energy',
         'handler': lambda x: pandas.Series(x, dtype=PintType('eV'))
        },
        {
         'calc_name': 'generic',
         'prop_name': 'natoms',
         'internal_name': 'natoms',
         'handler': lambda x: pandas.Series(ureg.Quantity(x, 'dimensionless'))
        },
        {
         'calc_name': 'generic',
         'prop_name': 'forces',
         'internal_name': 'forces',
         'handler': lambda x: pandas.Series(ureg.Quantity(f, EV_PER_ANG) for f in x)
        },
        {
         'calc_name': 'generic',
         'prop_name': 'energies',
         'internal_name': 'energies',
         'handler': lambda x: pandas.Series(ureg.Quantity(e, 'eV') for e in x)
        },
        {
         'calc_name': 'generic',
         'prop_name': 'free_energy',
         'internal_name': 'free_energy',
         'handler': lambda x: pandas.Series(x, dtype=PintType('eV'))
        },
        {
         'calc_name': 'generic',
         'prop_name': 'stress',
         'internal_name': 'stress',
         'handler': lambda x: pandas.Series(ureg.Quantity(f, 'eV / angstrom**3') for f in x)
        },
        {
         'calc_name': 'generic',
         'prop_name': 'stresses',
         'internal_name': 'stresses',
         'handler': lambda x: pandas.Series(ureg.Quantity(f, 'eV / angstrom**3') for f in x)
        },
        {
         'calc_name': 'generic',
         'prop_name': 'trajectory',
         'internal_name': 'trajectory',
         'handler': lambda x: pandas.Series(x, dtype='object')
        },
        {
         'calc_name': 'generic',
         'prop_name': 'rmsd',
         'internal_name': 'rmsd',
         'handler': lambda x: pandas.Series(x, dtype=PintType('angstrom'))
        },
        {
         'calc_name': 'generic',
         'prop_name': 'rdf',
         'internal_name': 'rdf',
         'handler': lambda x: pandas.Series(ureg.Quantity(i) for i in x)
        },
        {
         'calc_name': 'generic',
         'prop_name': 'rdf_distance',
         'internal_name': 'rdf_distance',
         'handler': lambda x: pandas.Series(ureg.Quantity(i, 'angstrom') for i in x)
        },
        {
         'calc_name': 'lj',
         'prop_name': 'energy',
         'internal_name': 'energy',
         'handler': lambda x: pandas.Series(x, dtype=PintType('eV'))
        },
        {
         'calc_name': 'lj',
         'prop_name': 'forces',
         'internal_name': 'forces',
         'handler': lambda x: pandas.Series(ureg.Quantity(i, EV_PER_ANG) for i in x)
        },
        {
         'calc_name': 'emt',
         'prop_name': 'energy',
         'internal_name': 'energy',
         'handler': lambda x: pandas.Series(x, dtype=PintType('eV'))
        },
        {
         'calc_name': 'emt',
         'prop_name': 'forces',
         'internal_name': 'forces',
         'handler': lambda x: pandas.Series(ureg.Quantity(i, EV_PER_ANG) for i in x)
        },
        {
         'calc_name': 'vasp',
         'prop_name': 'energy',
         'internal_name': 'energy',
         'handler': lambda x: pandas.Series(x, dtype=PintType('eV'))
        },
        {
         'calc_name': 'vasp',
         'prop_name': 'dipole',
         'internal_name': 'dipole',
         'handler': lambda x: pandas.Series(ureg.Quantity(i, EC_ANG) for i in x)
        },
        {
         'calc_name': 'vasp',
         'prop_name': 'forces',
         'internal_name': 'forces',
         'handler': lambda x: pandas.Series(ureg.Quantity(i, EV_PER_ANG) for i in x)
        },
        {
         'calc_name': 'vasp',
         'prop_name': 'vibrational_energies',
         'handler': vasp_vibrational_energies_handler
        },
        {
         'calc_name': 'vasp',
         'prop_name': 'energy_minimum',
         'handler': vasp_energy_minimum_handler
        },
        {
         'calc_name': 'vasp',
         'prop_name': 'transition_state',
         'handler': vasp_transition_state_handler
        },
        {
         'calc_name': 'turbomole',
         'prop_name': 'energy',
         'internal_name': 'total energy',
         'handler': lambda x: pandas.Series(x, dtype=PintType('eV'))
        },
        {
         'calc_name': 'turbomole',
         'prop_name': 'dipole',
         'internal_name': 'electric dipole moment',
         'handler': tm_dipole_handler,
        },
        {
         'calc_name': 'turbomole',
         'prop_name': 'forces',
         'internal_name': 'energy gradient',
         'handler': lambda x: pandas.Series(-ureg.Quantity(i, EV_PER_ANG) for i in x)
        },
        {
         'calc_name': 'turbomole',
         'prop_name': 'vibrational_energies',
         'internal_name': 'vibrational spectrum',
         'handler': tm_vibrational_energies_handler
        },
        {
         'calc_name': 'turbomole',
         'prop_name': 'energy_minimum',
         'internal_name': 'vibrational spectrum',
         'handler': tm_energy_minimum_handler
        },
        {
         'calc_name': 'turbomole',
         'prop_name': 'transition_state',
         'internal_name': 'vibrational spectrum',
         'handler': tm_transition_state_handler
        },
    ]
)


def get_ase_property(calc_name, prop_name, results, calcs=None):
    """convert a list of dictionaries into series of a specified property"""
    # todo: remove calc_name, results and internal name: delegate all to handler
    dfr = ase_p_df[(ase_p_df['calc_name'] == calc_name) & (ase_p_df['prop_name'] == prop_name)]
    msg = f'no property "{prop_name}" found for calculator "{calc_name}"'
    if len(dfr['handler']) == 0:
        raise PropertyError(msg)
    handler_func = next(iter(dfr['handler']))
    internal_name = next(iter(dfr['internal_name']))
    try:
        prop_results = [r[internal_name] for r in results]
    except KeyError:
        return handler_func(calcs)
    return handler_func(prop_results)


class RMSD(IOContext):
    """A wrapper algorithm to calculate root mean square deviation"""
    results = None

    def __init__(self, atoms):
        self.atoms_list = [atoms] if isinstance(atoms, ase.Atoms) else atoms

    def run(self, reference, adjust=True):
        """Calculate the root mean square deviation (RMSD) between a structure
           and a reference"""
        assert len(reference) == 1
        rmsd = []
        for atoms in self.atoms_list:
            ref_atoms = reference.to_ase()[0]
            if adjust:
                minimize_rotation_and_translation(ref_atoms, atoms)
            rmsd.append(numpy.sqrt(numpy.mean((numpy.linalg.norm(atoms.get_positions()
                                   - ref_atoms.get_positions(), axis=1))**2, axis=0)))
        self.results = {'rmsd': numpy.mean(rmsd), 'output_structure': self.atoms_list}
        return True


class RDF(IOContext):
    """A wrapper algorithm to calculate radial distribution function"""
    results = None
    analysis = None

    def __init__(self, atoms):
        self.atoms_list = [atoms] if isinstance(atoms, ase.Atoms) else atoms
        if any(sum(sum(a.cell)) == 0 for a in self.atoms_list):
            msg = 'the structure cell must have at least one non-zero vector'
            raise RuntimeValueError(msg)

    def run(self, rmax=None, nbins=40, neighborlist=None, neighborlist_pars=None,
            elements=None):
        """Calculate the radial distribution function for a structure"""
        if len(neighborlist_pars):
            neighborlist_pars = next(neighborlist_pars.iterrows())[1].to_dict()
        else:
            neighborlist_pars = {}
        self.analysis = Analysis(self.atoms_list, neighborlist, **neighborlist_pars)
        rmax = rmax or 0.49*max(max(a.cell.lengths()) for a in self.atoms_list)
        ret = self.analysis.get_rdf(rmax, nbins, elements=elements, return_dists=True)
        self.results = {'rdf': numpy.mean([a for a, b in ret], axis=0),
                        'rdf_distance': numpy.mean([b for a, b in ret], axis=0)}
        return True


class AMMLObject:
    """base class for all AMML objects"""


class AMMLStructure(AMMLObject):
    """"custom AMML Structure class"""
    intrinsics = ('name', 'kinetic_energy', 'temperature', 'distance_matrix',
                  'chemical_formula', 'number_of_atoms', 'cell_volume',
                  'center_of_mass', 'radius_of_gyration', 'moments_of_inertia',
                  'angular_momentum')

    def __init__(self, tab, name=None):
        if 'pbc' in tab and 'cell' not in tab:
            for pbc in tab['pbc'].values:
                if any(pbc):
                    raise RuntimeValueError('cell must be specified with pbc')
        self.name = name
        self.tab = tab

    def __getitem__(self, key):
        if isinstance(key, int):
            dfr = self.tab.iloc[[key]]
            return tuple(next(dfr.itertuples(index=False, name=None)))
        if isinstance(key, str):
            if key in self.intrinsics:
                return getattr(self, key)
            return self.tab[key]
        if isinstance(key, slice):
            return self.__class__(self.tab[key], self.name)
        raise TypeError('unknown key type')

    def __len__(self):
        return len(self.tab)

    @cached_property
    def kinetic_energy(self):
        """get the kinetic energy of the nuclei"""
        kin = self.to_ase().apply(lambda x: x.get_kinetic_energy())
        return pandas.Series(kin, dtype=PintType('eV'), name='kinetic_energy')

    @cached_property
    def temperature(self):
        """get the temperature"""
        temp = self.to_ase().apply(lambda x: x.get_temperature())
        return pandas.Series(temp, dtype=PintType('kelvin'), name='temperature')

    @cached_property
    def distance_matrix(self):
        """get the matrix of interatomic distances (distance matrix)"""
        dis = self.to_ase().apply(lambda x: x.get_all_distances(mic=True))
        return pandas.Series(dis, dtype=PintType('angstrom'), name='distance_matrix')

    @cached_property
    def chemical_formula(self):
        """get chemical formula as a string based on the chemical symbols"""
        chem_formula = self.to_ase().apply(lambda x: x.get_chemical_formula())
        return pandas.Series(chem_formula, name='chemical_formula')

    @cached_property
    def number_of_atoms(self):
        """get number of atoms"""
        natoms = self.to_ase().apply(len)
        return pandas.Series(natoms, name='number_of_atoms')

    @cached_property
    def cell_volume(self):
        """get volume of the unit cell"""
        try:
            vol = self.to_ase().apply(lambda x: x.get_volume())
        except ValueError as err:
            if 'volume not defined' in str(err):
                raise RuntimeValueError(str(err)) from err
            raise err
        return pandas.Series(vol, dtype=PintType('angstrom**3'), name='cell_volume')

    @cached_property
    def center_of_mass(self):
        """get the center of mass"""
        com = self.to_ase().apply(lambda x: x.get_center_of_mass())
        return pandas.Series(com, dtype=PintType('angstrom'), name='center_of_mass')

    @cached_property
    def radius_of_gyration(self):
        """get the radius of gyration"""
        def rogf(pos):
            centroid = numpy.mean(pos, axis=0)
            norm_sqr = (numpy.linalg.norm(pos-centroid, axis=1))**2
            return numpy.sqrt(numpy.mean(norm_sqr, axis=0))
        rog = self.to_ase().apply(lambda x: rogf(x.get_positions()))
        return pandas.Series(rog, dtype=PintType('angstrom'), name='radius_of_gyration')

    @cached_property
    def moments_of_inertia(self):
        """get the moments of inertia along the principal axes"""
        moi = self.to_ase().apply(lambda x: x.get_moments_of_inertia())
        unit = 'amu * angstrom**2'
        return pandas.Series(moi, dtype=PintType(unit), name='moments_of_inertia')

    @cached_property
    def angular_momentum(self):
        """get the total angular momentum with respect to the center of mass"""
        ang = self.to_ase().apply(lambda x: x.get_angular_momentum())
        unit = '( amu * eV ) ** (1/2) * angstrom'
        return pandas.Series(ang, dtype=PintType(unit), name='angular_momentum')

    def to_ase_file(self, filename):
        """store series of ase.Atoms objects to a file in supported format"""
        atoms_objs = self.to_ase()
        write(images=atoms_objs, filename=filename)

    def to_ase(self):
        """create a series of ase.Atoms objects from a structure dataframe"""
        dfr_ase = self.get_ase_atoms_dataframe()
        series = dfr_ase.apply(lambda row: ase.Atoms(**row.to_dict()), axis=1)
        return series.rename(self.name, inplace=True)

    def get_ase_atoms_dataframe(self):
        """return a unitless atoms dataframe from a structure dataframe with units"""
        dfr = self.tab
        dfr_ase = pandas.DataFrame()
        dfr_ase['symbols'] = dfr['atoms'].apply(lambda x: x.symbols.to_numpy())
        if 'cell' in dfr:
            dfr_ase['cell'] = dfr['cell'].apply(lambda x: x.to('angstrom').magnitude)
        else:
            dfr_ase[['cell']] = None

        dfr_ase['pbc'] = dfr['pbc'].to_numpy() if 'pbc' in dfr else None

        def xyz2pos(atoms):
            xcoord = get_pint_series(atoms['x']).pint.to('angstrom').values.data
            ycoord = get_pint_series(atoms['y']).pint.to('angstrom').values.data
            zcoord = get_pint_series(atoms['z']).pint.to('angstrom').values.data
            return numpy.array([xcoord, ycoord, zcoord]).transpose()

        def pxpypz2momenta(atoms):
            if 'px' not in atoms:
                return None
            units = '( amu * eV ) ** (1/2)'
            xcoord = get_pint_series(atoms['px']).pint.to(units).values.data
            ycoord = get_pint_series(atoms['py']).pint.to(units).values.data
            zcoord = get_pint_series(atoms['pz']).pint.to(units).values.data
            return numpy.array([xcoord, ycoord, zcoord]).transpose()

        dfr_ase['positions'] = dfr['atoms'].apply(xyz2pos)
        dfr_ase['momenta'] = dfr['atoms'].apply(pxpypz2momenta)
        dfr_ase['tags'] = dfr['atoms'].apply(lambda x: x.tags.to_numpy() if 'tags' in x else None)
        return dfr_ase

    @classmethod
    def from_ase(cls, atoms, name=None):
        """create an AMML object from an ASE Atoms object"""
        if isinstance(atoms, ase.Atoms):
            return cls(get_structure_dataframe(atoms), name)
        assert isinstance(atoms, (list, tuple, pandas.Series))
        atoms_dfs = [get_structure_dataframe(a) for a in atoms]
        return cls(pandas.concat(atoms_dfs, ignore_index=True), name)

    @classmethod
    def from_ase_file(cls, filename):
        """create an AMML Structure object from a file in an ASE-supported format"""
        try:
            structs = ase.io.read(filename, index=':')
        except Exception as err:  # broad exception due to ase.io.read
            msg = f'{err.__class__.__name__}: {str(err)}'
            raise StructureInputError(msg) from err
        struct_dfs = [get_structure_dataframe(s) for s in structs]
        return cls(pandas.concat(struct_dfs, ignore_index=True))

    @classmethod
    def from_series(cls, series):
        """create an AMML Structure object from series of Structure objects"""
        tabs = (s.tab for s in series)
        tab = pandas.concat(tabs, axis='index', ignore_index=True)
        return cls(tab, name=series[0].name)


class AMMLMethod(AMMLObject):
    """base class for AMML Calculator and Algorithm classes"""
    def __init__(self, name, parameters):
        self.name = name
        self.parameters = parameters
        if self.parameters is None or len(self.parameters) == 0:
            param_spec = spec[self.name]['params']
            par_def = {k: v.get('default') for k, v in param_spec.items()}
            self.parameters = pandas.DataFrame([par_def])

    def __getitem__(self, key):
        if isinstance(key, int):
            dfr = self.parameters.iloc[[key]]
            return tuple(next(dfr.itertuples(index=False, name=None)))
        if isinstance(key, str):
            return getattr(self, key)
        if isinstance(key, slice):
            return self.__class__(self.name, self.parameters[key])
        raise TypeError(f'unknown key type {type(key)}')


class Calculator(AMMLMethod):
    """custom AMML Calculator class"""
    def __init__(self, name, parameters, pinning=None, version=None, task=None):
        super().__init__(name, parameters)
        self.pinning = pinning
        self.version = version
        self.task = task  # todo: adapt calc parameters due to task

    def __getitem__(self, key):
        if isinstance(key, (int, str)):
            return super().__getitem__(key)
        if isinstance(key, slice):
            return self.__class__(self.name, self.parameters[key], self.pinning,
                                  self.version)
        raise TypeError(f'unknown key type {type(key)}')

    def to_ase(self):
        """create a series of ASE Calculator objects"""
        calc_class = get_calculator_class(self.name)
        calc_list = []
        for _, row in self.parameters.iterrows():
            calc_params = dict(row)
            units = get_params_units(self.name, calc_params)
            calc_list.append(calc_class(**get_params_magnitudes(calc_params, units)))
        return pandas.Series(calc_list, name='calc')

    @classmethod
    def from_ase(cls, ase_calc):
        """create an AMML Calculator object from an ASE Calculator object"""
        return cls(ase_calc.name.lower(), get_calculator_dataframe(ase_calc))

    def requires_dof(self):
        """determine whether the calculator requires changes of degrees of freedom"""
        if self.task is not None:
            return self.task != 'single point'
        return None

    def run(self, struct, constrs=None):
        """runner for objects with length 1"""
        assert len(struct.tab) == len(self.parameters) == 1
        calc_ase = self.to_ase()[0]
        struct_ase = ase.Atoms(struct.to_ase()[0])
        struct_ase.constraints = constrs
        calc_ase.calculate(struct_ase)
        if hasattr(calc_ase, 'converged'):
            if not calc_ase.converged:
                msg = f'calculation with {self.name} did not converge'
                raise ConvergenceError(msg)
        return calc_ase


class Algorithm(AMMLMethod):
    """custom AMML Algorithm class"""
    def __init__(self, name, parameters, many_to_one=False):
        super().__init__(name, parameters)
        self.many_to_one = many_to_one
        module = importlib.import_module(spec[self.name]['module'])
        self._class = getattr(module, spec[self.name]['class'])
        self.params = {k: [] for k in ('class', 'run', 'attach')}
        param_spec = spec[self.name]['params']
        par_def = {k: v.get('default') for k, v in param_spec.items()}
        par_mth = {k: v.get('method') for k, v in param_spec.items()}
        for _, row in self.parameters.iterrows():
            params = {}
            params.update(par_def)
            params.update(dict(row))
            if params.get('trajectory') or params.get('logfile'):
                basename = uuid.uuid4().hex
            if params.get('trajectory'):
                fname = basename + '.traj'
                params['trajectory'] = os.path.join(os.path.abspath(os.getcwd()), fname)
            if params.get('logfile'):
                fname = basename + '.log'
                params['logfile'] = os.path.join(os.path.abspath(os.getcwd()), fname)
            units = get_params_units(self.name, params)
            ase_pars = get_params_magnitudes(params, units)
            for tp in ('class', 'run', 'attach'):
                pars = {k: v for k, v in ase_pars.items() if par_mth[k] == tp}
                self.params[tp].append(pars)

    def __getitem__(self, key):
        if isinstance(key, (int, str)):
            return super().__getitem__(key)
        if isinstance(key, slice):
            return self.__class__(self.name, self.parameters[key], many_to_one=self.many_to_one)
        raise TypeError(f'unknown key type {type(key)}')

    def run(self, struct, calc=None, constrs=None):
        """the algorithm runner, process objects with length 1"""
        assert len(self.params['class']) == len(self.params['run']) == 1
        assert len(self.params['attach']) == 1
        atoms_list = [ase.Atoms(a) for a in struct.to_ase()]
        for atoms in atoms_list:
            atoms.constraints = constrs
        if self.many_to_one:
            struct_ase = atoms_list
        else:
            assert len(struct.tab) == 1
            struct_ase = atoms_list[0]
        if calc is not None:
            assert len(calc.parameters) == 1
            calc_ase = calc.to_ase()[0]
            if self.many_to_one:
                for atoms in struct_ase:
                    atoms.calc = calc_ase
            else:
                struct_ase.calc = calc_ase
        cls_params = dict(self.params['class'][0])
        traj_file = cls_params.pop('trajectory', None)
        with self._class(struct_ase, **cls_params) as algo_obj:
            if traj_file:
                with TrajectoryWriter(traj_file, atoms=struct_ase) as traj:
                    algo_obj.attach(traj, **self.params['attach'][0])
                    converged = algo_obj.run(**self.params['run'][0])
            else:
                converged = algo_obj.run(**self.params['run'][0])
        if not converged:
            msg = f'calculation with {self.name} did not converge'
            raise ConvergenceError(msg)
        results = getattr(algo_obj, 'results', {})
        results['output_structure'] = struct_ase
        if calc is not None:
            results['energy'] = struct_ase.get_potential_energy()
            results['forces'] = struct_ase.get_forces()
        if traj_file:
            results['trajectory'] = Trajectory.from_file(traj_file, name=struct.name)
        return results


class Property(AMMLObject):
    """custom AMML Property class"""
    _props_algo = ['rmsd', 'rdf_distance', 'rdf', 'trajectory']

    def __init__(self, names, structure, calculator=None, algorithm=None,
                 constraints=None, results=None):
        self.names = names
        self.structure = structure
        self.calculator = calculator
        self.algorithm = algorithm
        if constraints:
            if not all(len(c.fixed) == len(a) for c in constraints for a in structure.tab.atoms):
                msg = ('The list of fixed/non-fixed atoms in constraints and '
                       'atoms in structure have different lengths')
                raise RuntimeValueError(msg)
            self.constraints = constraints
        else:
            self.constraints = []
        self.dof_vector, self.dof_number = self.get_dof()
        if self.calculator:
            self.requires_dof = self.calculator.requires_dof()
            if self.requires_dof is not None:
                if self.requires_dof and self.dof_number == 0:
                    msg = 'All degrees of freedom frozen. Hint: check task and constraints.'
                    raise RuntimeValueError(msg)

        self.results = results if results is not None else self.get_results()

    def __getitem__(self, key):
        keys = ('names', 'calculator', 'structure', 'algorithm', 'constraints',
                'results')
        if isinstance(key, int):
            dfr = self.results.iloc[[key]]
            return tuple(next(dfr.itertuples(index=False, name=None)))
        if isinstance(key, str):
            if key in keys:
                return getattr(self, key)
            if key == 'output_structure':
                return AMMLStructure.from_series(self.results.output_structure)
            try:
                return getattr(self.results, key)
            except AttributeError as err:
                raise PropertyError(f'property "{key}" not available') from err
        if isinstance(key, slice):
            struct = merge_structures(self.results.structure[key])
            if self.calculator:
                calc = merge_calculators(self.results.calculator[key])
            else:
                assert all(c is None for c in self.results.calculator[key])
                calc = None
            if self.algorithm:
                algo = merge_algorithms(self.results.algorithm[key])
            else:
                assert all(a is None for a in self.results.algorithm[key])
                algo = None
            return self.__class__(self.names, struct, calculator=calc,
                                  algorithm=algo, constraints=self.constraints,
                                  results=self.results[key])
        raise TypeError('unknown key type')

    def get_dof(self):
        """return the non-frozen nuclear degrees of freedom"""
        atoms = self.structure[0:1].to_ase()[0]
        if self.constraints:
            new_pos = numpy.array(atoms.positions)
            for ind, (pbc, vec) in enumerate(zip(atoms.pbc, atoms.cell)):
                if pbc:
                    new_pos += 0.9*vec
                else:
                    new_pos[:, ind] += 0.9
            wrap_positions(new_pos, atoms.cell, atoms.pbc)
            for constr in self.constraints:
                for constr_ in constr.to_ase():
                    constr_.adjust_positions(atoms, new_pos)
            epsilon = numpy.finfo(numpy.float64).eps
            dof = numpy.abs(atoms.positions-new_pos) > epsilon
        else:
            dof = numpy.full((len(atoms), 3), True)
        return dof, numpy.sum(dof)

    def get_results_df(self):
        """create a dataframe for results, populate with struct, calc, algo"""
        calc_it = self.calculator if self.calculator else [None]
        algo_it = self.algorithm if self.algorithm else [None]
        if self.algorithm and self.algorithm.many_to_one:
            stru_it = [self.structure]
        else:
            stru_it = self.structure

        def gen_func():
            columns_iter = itertools.product(calc_it, algo_it, stru_it)
            for calc, algo, struct in columns_iter:
                if calc is None:
                    calc_amml = None
                else:
                    calc_ = self.calculator
                    calc_df = pandas.DataFrame([dict(zip(calc_.parameters, calc))])
                    calc_amml = Calculator(parameters=calc_df, name=calc_.name,
                                           pinning=calc_.pinning, version=calc_.version)
                if algo is None:
                    algo_amml = None
                else:
                    algo_df = pandas.DataFrame([dict(zip(self.algorithm.parameters, algo))])
                    algo_amml = Algorithm(self.algorithm.name, algo_df, self.algorithm.many_to_one)

                if self.algorithm and self.algorithm.many_to_one:
                    struct_amml = struct
                else:
                    struct_df = pandas.DataFrame([dict(zip(self.structure.tab, struct))])
                    struct_amml = AMMLStructure(struct_df, self.structure.name)
                yield struct_amml, calc_amml, algo_amml
        columns = ['structure', 'calculator', 'algorithm']
        return pandas.DataFrame(gen_func(), columns=columns)

    def get_results(self):
        """create a dataframe with properties calculated using ASE"""
        df = self.get_results_df()
        constrs = []
        for constr in self.constraints:
            constrs.extend(constr.to_ase())

        def apply_algo(struct, calc, algo):
            if self.calculator:
                return algo.run(struct, calc, constrs=constrs)
            return algo.run(struct, constrs=constrs)

        def apply_calc(struct, calc, _):
            return calc.run(struct, constrs=constrs)

        def apply_func(df, func):
            return func(df.structure, df.calculator, df.algorithm)

        def get_struct_from_calc(calc):
            return AMMLStructure.from_ase(calc.get_atoms(), self.structure.name)

        def get_struct_from_algo(dct):
            return AMMLStructure.from_ase(dct['output_structure'], self.structure.name)

        if self.algorithm:
            df['results'] = df.apply(lambda x: apply_func(x, apply_algo), axis=1)
            df['output_structure'] = df['results'].apply(get_struct_from_algo)
            for prop in self.names:
                method = 'generic' if prop in self._props_algo else self.calculator.name
                df[prop] = get_ase_property(method, prop, df['results'])
            df.drop(columns=['results'], inplace=True)
        elif self.calculator:
            df['calc'] = df.apply(lambda x: apply_func(x, apply_calc), axis=1)
            df['results'] = df['calc'].apply(lambda x: x.results)
            df['output_structure'] = df['calc'].apply(get_struct_from_calc)
            for prop in self.names:
                df[prop] = get_ase_property(self.calculator.name, prop,
                                            df['results'], calcs=df['calc'])
            df.drop(columns=['calc', 'results'], inplace=True)
        else:
            raise NotImplementedError('pure properties not implemented')
        return df


class Constraint(AMMLObject):
    """custom AMML Constraint class"""
    def __init__(self, name, **kwargs):
        assert name in ['FixedAtoms', 'FixedLine', 'FixedPlane']
        self.name = name
        self.kwargs = kwargs
        self.fixed = kwargs['fixed']
        self.indices = self.fixed[self.fixed].index.values
        if name in ['FixedLine', 'FixedPlane']:
            self.direction = kwargs['direction']

    def to_ase(self):
        """return ASE constraint objects"""
        if self.name == 'FixedAtoms':
            return [ase.constraints.FixAtoms(indices=self.indices)]
        if self.name == 'FixedLine':
            cls = ase.constraints.FixedLine
        elif self.name == 'FixedPlane':
            cls = ase.constraints.FixedPlane
        direction = [c.magnitude for c in self.direction.tolist()]
        return [cls(i, direction=direction) for i in self.indices]

    @classmethod
    def from_ase(cls, constr, natoms):
        """convert an ASE constraint object into AMML constraint"""
        indices = constr.get_indices()
        fixed = pandas.Series(i in indices for i in range(natoms))
        direction = getattr(constr, 'direction', None)
        return cls(constr.__class__.__name__, fixed=fixed, direction=direction)


@dataclass
class Trajectory(AMMLObject):
    """custom AMML trajectory class"""
    description: pandas.DataFrame = None
    structure: AMMLStructure = None
    properties: pandas.DataFrame = None
    constraints: list[Constraint] = field(default_factory=list)
    filename: str = None

    @classmethod
    def from_file(cls, filename, name=None):
        """create an AMML Trajectory object from an ASE trajectory file"""
        with TrajectoryReader(filename) as traj:
            ase_description = traj.description
            ase_structs = list(traj)
            ase_constraints = traj.constraints
        for atoms in ase_structs:
            assert hasattr(atoms, 'calc')
            assert isinstance(atoms.calc, SinglePointCalculator)
        structure = AMMLStructure.from_ase(ase_structs, name=name)
        description = pandas.DataFrame()
        description['type'] = pandas.Series(ase_description['type'])
        if 'optimizer' in ase_description:
            algo = description['optimizer'] = ase_description['optimizer']
        elif 'md-type' in ase_description:
            algo = description['md-type'] = ase_description['md-type']
        params = {k: v for k, v in ase_description.items() if k in spec[algo]['params']}
        for ukey, uval in get_params_units(algo, params).items():
            if uval is not None:
                mag = numpy.nan if ase_description[ukey] is None else ase_description[ukey]
                description[ukey] = ureg.Quantity(mag, uval)
            else:
                description[ukey] = ase_description[ukey]
        props_ase = [a.calc.export_properties() for a in ase_structs]
        properties = pandas.DataFrame()
        for key in props_ase[0].keys():
            properties[key] = get_ase_property('generic', key, props_ase)
        # this is because in case of no constraints a string '[]' is stored in the trajectory (!?)
        ase_constraints = ase_constraints if not isinstance(ase_constraints, str) else None
        if ase_constraints:
            constraints = []
            for cons, natoms in zip(ase_constraints, properties['natoms']):
                constraints.append([Constraint.from_ase(c, natoms) for c in cons])
        else:
            constraints = [[]]*len(traj)
        constraints = pandas.Series(constraints, name='constraints')
        assert len(structure) == len(properties) == len(constraints)
        return cls(description, structure, properties, constraints, filename)

    def __getitem__(self, key):
        if isinstance(key, int):
            props = self.properties.iloc[[key]].itertuples(index=False, name=None)
            return tuple((*self.structure[key], *props))
        if isinstance(key, str):
            return getattr(self, key)
        if isinstance(key, slice):
            return self.__class__(self.description, self.structure[key],
                                  self.properties.iloc[key], self.constraints[key],
                                  self.filename)
        raise TypeError(f'unknown key type {type(key)}')


class NeighborList(AMMLObject):
    """custom AMML NeighborList class"""
