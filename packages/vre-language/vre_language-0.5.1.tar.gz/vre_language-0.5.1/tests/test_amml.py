"""
tests for amml data structures and operations
"""
import os
import pytest
from textx import get_children_of_type
from textx.exceptions import TextXError
from virtmat.language.utilities.types import typemap
from virtmat.language.utilities.amml import AMMLStructure


@pytest.fixture(name='water_yaml')
def water_yaml_fixture(tmp_path):
    """path to water.yaml file"""
    return os.path.join(tmp_path, 'water.yaml')


@pytest.fixture(name='water_cif')
def water_cif_fixture(tmp_path):
    """path to water.cif file"""
    return os.path.join(tmp_path, 'water.cif')


@pytest.fixture(name='calc_yaml')
def water_calc_fixture(tmp_path):
    """path to calc.yaml file"""
    return os.path.join(tmp_path, 'calc.yaml')


def test_amml_structure_literal(meta_model, model_kwargs, water_yaml, water_cif):
    """test AMML structure literal and I/O"""
    if 'model_instance' in model_kwargs:
        pytest.skip('test does not work in workflow mode (I/O race condition)')

    inp = ("water = Structure ("
           "          (atoms: ((symbols: 'O', 'H', 'H'),"
           "                   (x: 0., 0., 0.) [nm],"
           "                   (y: 0., 0.763239, -0.763239) [angstrom],"
           "                   (z: 0.119262, -0.477047, -0.477047) [angstrom],"
           "                   (tags: 1, 0, 0),"
           "                   (masses: 16., 1., 1.) [amu]"
           "                  )"
           "          ),"
           "          (cell: [[2., 0., 0.], [0., 2., 0.], [0., 0., 2.]] [bohr]),"
           "          (pbc: [false, false, true])"
           "        )\n"
           "water to file \'" + water_yaml + "\'\n"
           "water to file \'" + water_cif + "\'\n"
           "water_1 = Structure from file \'" + water_yaml + "\'\n"
           "water_2 = Structure from file \'" + water_cif + "\'")
    prog = meta_model.model_from_str(inp, **model_kwargs)
    var_list = get_children_of_type('Variable', prog)
    water_var = next(v for v in var_list if v.name == 'water')
    assert issubclass(water_var.type_, typemap['AMMLStructure'])
    assert isinstance(water_var.value, typemap['AMMLStructure'])
    water1_var = next(v for v in var_list if v.name == 'water_1')
    water2_var = next(v for v in var_list if v.name == 'water_2')
    assert water2_var.value['atoms'][0].symbols.tolist() == ['O', 'H', 'H']
    assert water1_var.value.name == water_var.value.name
    tab = water1_var.value.tab
    tabref = water_var.value.tab
    assert tab.atoms[0].symbols.tolist() == tabref.atoms[0].symbols.tolist()
    assert tab.atoms[0].x.tolist() == tabref.atoms[0].x.tolist()
    assert tab.atoms[0].y.tolist() == tabref.atoms[0].y.tolist()
    assert tab.atoms[0].z.tolist() == tabref.atoms[0].z.tolist()
    assert tab.atoms[0].tags.tolist() == tabref.atoms[0].tags.tolist()
    assert tab.atoms[0].masses.tolist() == tabref.atoms[0].masses.tolist()
    assert tab.cell[0].data.tolist() == tabref.cell[0].data.tolist()
    assert tab.pbc[0].data.tolist() == tabref.pbc[0].data.tolist()


def test_amml_calculator_literal(meta_model, model_kwargs, calc_yaml):
    """test AMML calculator literal and I/O"""
    inp = ("calc = Calculator vasp ("
           "     (algo: 'Fast'),"
           "     (ediff: 1e-06) [eV],"
           "     (ediffg: -0.01) [eV/angstrom],"
           "     (encut: 400.0) [eV],"
           "     (ibrion: 2),"
           "     (icharg: 2),"
           "     (isif: 2),"
           "     (ismear: 0),"
           "     (ispin: 2),"
           "     (istart: 0),"
           "     (kpts: [5, 5, 1]),"
           "     (lcharg: false),"
           "     (lreal: 'Auto'),"
           "     (lwave: false),"
           "     (nelm: 250),"
           "     (nsw: 1500),"
           "     (potim: 0.1),"
           "     (prec: 'Normal'),"
           "     (sigma: 0.1) [eV],"
           "     (xc: 'PBE')"
           ");"
           "calc to file \'" + calc_yaml + "\'")
    prog = meta_model.model_from_str(inp, **model_kwargs)
    var_list = get_children_of_type('Variable', prog)
    calc_var = next(v for v in var_list if v.name == 'calc')
    assert issubclass(calc_var.type_, typemap['AMMLCalculator'])
    assert isinstance(calc_var.value, typemap['AMMLCalculator'])


def test_amml_property_literal(meta_model, model_kwargs):
    """test AMML property literal and I/O"""
    inp = ("h2o = Structure water ("
           "        (atoms: ((symbols: 'O', 'H', 'H'),"
           "                 (x: 0., 0., 0.) [nm],"
           "                 (y: 0., 0.763239, -0.763239) [angstrom],"
           "                 (z: 0.119262, -0.477047, -0.477047) [angstrom]"
           "                )"
           "        ),"
           "        (cell: [[10., 0., 0.], [0., 10., 0.], [0., 0., 10.]] [angstrom]),"
           "        (pbc: [true, true, true])"
           "      );"
           "calc = Calculator vasp >= 5.4.4 ("
           "          (algo: 'Fast'),"
           "          (ediff: 1e-06) [eV],"
           "          (ediffg: -0.005) [eV/angstrom],"
           "          (encut: 400.0) [eV],"
           "          (ibrion: 2),"
           "          (icharg: 2),"
           "          (isif: 2),"
           "          (ismear: 0),"
           "          (ispin: 2),"
           "          (istart: 0),"
           "          (kpts: [5, 5, 1]),"
           "          (lcharg: false),"
           "          (lreal: 'Auto'),"
           "          (lwave: false),"
           "          (nelm: 250),"
           "          (nsw: 1500),"
           "          (potim: 0.1),"
           "          (prec: 'Normal'),"
           "          (sigma: 0.1) [eV],"
           "          (xc: 'PBE')"
           "       );"
           "props = Property energy, forces ((structure: h2o), (calculator: calc))")
    meta_model.model_from_str(inp, **model_kwargs)


def test_amml_property_access_properties(meta_model, model_kwargs):
    """test access to properties in an evaluated AMML property literal"""
    inp = ("epsilon_K = 119.8 [K];"
           "kB = 1. [boltzmann_constant];"
           "calc = Calculator lj ((sigma: 3.405) [angstrom], (epsilon: epsilon_K*kB));"
           "struct = Structure fcc_Ar4 ("
           "     (atoms: ("
           "       (symbols: 'Ar', 'Ar', 'Ar', 'Ar'),"
           "       (x: 0., 2.41, 2.41, 0.) [angstrom],"
           "       (y: 0., 2.41, 0., 2.41) [angstrom],"
           "       (z: 0., 0., 2.41, 2.41) [angstrom]"
           "      )"
           "     ),"
           "     (pbc: [true, true, true]),"
           "     (cell: [[4.82, 0., 0.], [0., 4.82, 0.], [0., 0., 4.82]] [angstrom])"
           ");"
           "prop = Property energy, forces ((calculator: calc), (structure: struct));"
           "print(calc, struct);"
           "print(prop);"
           "print(prop.energy);"
           "print(prop.forces); energy = prop.energy[0]")
    prog = meta_model.model_from_str(inp, **model_kwargs)
    print(prog.value)
    var_list = get_children_of_type('Variable', prog)
    energy = next(v for v in var_list if v.name == 'energy')
    assert issubclass(energy.type_, typemap['Quantity'])
    assert isinstance(energy.value, typemap['Quantity'])
    assert energy.value.units == 'electron_volt'
    assert energy.value.magnitude == pytest.approx(-0.16027557460638842)


def test_amml_property_slicing(meta_model, model_kwargs):
    """test amml property slicing"""
    inp = ("h2o = Structure water ("
           "     (atoms: ((symbols: 'O', 'H', 'H'),"
           "       (x: 0., 0., 0.) [nm],"
           "       (y: 0., 0.763239, -0.763239) [angstrom],"
           "       (z: 0.119262, -0.477047, -0.477047) [angstrom]"
           "      )"
           "     )"
           ");"
           "calc = Calculator emt ((restart: default), (fixed_cutoff: default)),"
           "                      task: single point;"
           "calc2 = Calculator emt ();"
           "props = Property energy, forces ((structure: h2o), (calculator: calc));"
           "props2 = Property energy, forces ((structure: h2o), (calculator: calc2));"
           "print(props[0]);"
           "print(props.calculator[0:1]);"
           "props_01 = props[0:1];"
           "print(props_01);"
           "print(props_01.structure);"
           "print(props_01.calculator);"
           "print(props2[0])\n")
    prog = meta_model.model_from_str(inp, **model_kwargs)
    print(prog.value)


def test_amml_constraints_properties(meta_model, model_kwargs):
    """test AMML property with AMML calculator and AMML constraints"""
    inp = ("h2o = Structure H2O ("
           "          (atoms: ((symbols: 'O', 'H', 'H'),"
           "                   (x: 6., 6.96504783, 5.87761163) [angstrom],"
           "                   (y: 6., 5.87761163, 6.96504783) [angstrom],"
           "                   (z: 6., 6.00000000, 6.00000000) [angstrom]"
           "                  )"
           "          ),"
           "          (cell: [[12., 0., 0.], [0., 12., 0.], [0., 0., 12.]] [angstrom]),"
           "          (pbc: [true, true, true])"
           ");"
           "h2 = Structure H2 ("
           "          (atoms: ((symbols: 'H', 'H'),"
           "               (x: 0., 0.) [angstrom],"
           "               (y: 0., 0.) [angstrom],"
           "               (z: 0., 1.) [angstrom]"
           "            )"
           "          ),"
           "          (cell: [[12., 0., 0.], [0., 12., 0.], [0., 0., 12.]] [angstrom]),"
           "          (pbc: [true, true, true])"
           ");"
           "calc = Calculator emt(), task: single point;"
           "calc2 = Calculator emt((fixed_cutoff: default, false));"
           "plane = FixedPlane normal to [0, 0, 1] where (fix: true, true, true);"
           "props = Property energy, forces ((structure: h2o), (calculator: calc),"
           "                                 (constraints: (plane,)));"
           "props2 = Property energy, forces ((structure: h2o), (calculator: calc2),"
           "                                  (constraints: (plane,)));"
           "print(plane);"
           "print(props.structure.name, props.energy);"
           "print(props2.structure.name, props2.energy)")
    prog = meta_model.model_from_str(inp, **model_kwargs)
    print(prog.value)


def test_amml_property_inconsistent_constraints(meta_model, model_kwargs):
    """test AMML property with AMML structure and inconsistent AMML constraints"""
    inp = ("h2 = Structure H2 ("
           "          (atoms: ((symbols: 'H', 'H'),"
           "               (x: 0., 0.) [angstrom],"
           "               (y: 0., 0.) [angstrom],"
           "               (z: 0., 1.) [angstrom]"
           "            )"
           "          )"
           ");"
           "calc = Calculator emt(default);"
           "constr = FixedAtoms where (fix: true, false, false);"
           "props = Property energy ((structure: h2), (calculator: calc),"
           "                         (constraints: (constr,)))\n")
    msg = ('The list of fixed/non-fixed atoms in constraints and atoms in '
           'structure have different lengths')
    with pytest.raises(TextXError, match=msg):
        meta_model.model_from_str(inp, **model_kwargs)


def test_amml_optimizer_algorithms(meta_model, model_kwargs):
    """test AMML optimizer algorithms"""
    inp = ("algo1 = Algorithm BFGS ((fmax: 1e-4) [hartree/bohr], (steps: 30));"
           "algo2 = Algorithm LBFGS ((fmax: 1e-2) [eV/angstrom], (trajectory: true));"
           "algo3 = Algorithm GPMin ((fmax: 0.005) [hartree/bohr], (steps: 30))\n"
           "algo4 = Algorithm FIRE ((steps: 30), (trajectory: true), (interval: 2));"
           "algo5 = Algorithm QuasiNewton ((fmax: 0.05) [eV/bohr], (steps: 30))\n"
           "algo6 = Algorithm BFGSLineSearch ((fmax: 0.0001) [hartree/bohr])\n"
           "algo7 = Algorithm LBFGSLineSearch ()\n"
           "algo8 = Algorithm MDMin ((trajectory: true), (dt: 0.01))")
    meta_model.model_from_str(inp, **model_kwargs)


def test_amml_optimizer_run(meta_model, model_kwargs):
    """test AMML optimizer algorithm runs"""
    inp = ("algo = Algorithm BFGS ((fmax: 1e-4) [hartree/bohr], (trajectory: true));"
           "h2o = Structure water (("
           "         atoms: ((symbols: 'O', 'H', 'H'),"
           "                 (x: 0., 0., 0.) [nm],"
           "                 (y: 0., 0.763239, -0.763239) [angstrom],"
           "                 (z: 0.119262, -0.477047, -0.477047) [angstrom])));"
           "calc = Calculator emt (), task: single point;"
           "constr = FixedAtoms where (fix: true, false, false);"
           "props = Property energy,"
           "                 forces,"
           "                 trajectory ((structure: h2o),"
           "                             (calculator: calc),"
           "                             (algorithm: algo),"
           "                             (constraints: (constr,)));"
           "energy = props.energy")
    prog = meta_model.model_from_str(inp, **model_kwargs)
    var_list = get_children_of_type('Variable', prog)
    energy = next(v for v in var_list if v.name == 'energy').value[0].to('eV').magnitude
    assert energy == pytest.approx(1.8789, 1e-3)


def test_amml_md_algorithms(meta_model, model_kwargs):
    """test AMML molecular dynamics algorithms"""
    inp = ("algo1 = Algorithm VelocityVerlet ((timestep: 1) [fs], (steps: 5),"
           "                                  (trajectory: true));"
           "algo2 = Algorithm Langevin ((timestep: 1) [fs], (steps: 5),"
           "                            (temperature_K: 300.) [K], (friction: 0.05 [1/fs]),"
           "                            (trajectory: true));"
           "algo3 = Algorithm NPT ((timestep: 1) [fs], (steps: 5), (temperature_K: 300.) [K],"
           "                       (externalstress: 1) [bar], (ttime: 25) [fs],"
           "                       (pfactor: (100 [GPa] * 75 [fs])**2), (trajectory: true));"
           "algo4 = Algorithm Andersen ((timestep: 5) [fs], (steps: 100),"
           "                            (temperature_K: 300.) [K], (andersen_prob: 0.005),"
           "                            (trajectory: true));"
           "algo5 = Algorithm NVTBerendsen ((timestep: 5) [fs], (steps: 100),"
           "                                (temperature_K: 300.) [K], (taut: 100) [fs],"
           "                                (trajectory: true));"
           "algo6 = Algorithm NPTBerendsen ((timestep: 5) [fs], (steps: 100),"
           "                                (temperature_K: 300.) [K], (pressure_au: 100 [bar]),"
           "                                (compressibility_au: 4.57e-5) [1/bar],"
           "                                (trajectory: true))")
    meta_model.model_from_str(inp, **model_kwargs)


def test_amml_property_resources(meta_model_wf, model_kwargs_wf, _res_config_loc):
    """test AMML property literal resources"""
    inp = ("h2o = Structure water ("
           "        (atoms: ((symbols: 'O', 'H', 'H'),"
           "                 (x: 0., 0., 0.) [nm],"
           "                 (y: 0., 0.763239, -0.763239) [angstrom],"
           "                 (z: 0.119262, -0.477047, -0.477047) [angstrom]"
           "                )"
           "        ),"
           "        (cell: [[10., 0., 0.], [0., 10., 0.], [0., 0., 10.]] [angstrom]),"
           "        (pbc: [true, true, true])"
           "      );"
           "calc = Calculator vasp >= 5.4.4 ();"
           "prop = Property energy, forces ((structure: h2o), (calculator: calc))"
           "       on 4 cores for 0.1 [hour]")
    pre_rocket = ('module purge; module use null; module load chem/vasp/5.4.4.pl2; '
                  'export VASP_COMMAND="$DO_PARALLEL $VASP_MPI"')
    prog = meta_model_wf.model_from_str(inp, **model_kwargs_wf)
    var_list = get_children_of_type('Variable', prog)
    var = next(v for v in var_list if v.name == 'prop')
    fw_ids = prog.lpad.get_fw_ids({'name': var.fireworks[0].name})
    assert len(fw_ids) == 1
    fw_spec = prog.lpad.get_fw_by_id(fw_ids[0]).spec
    assert '_category' in fw_spec
    assert fw_spec['_category'] == 'batch'
    assert '_queueadapter' in fw_spec
    qadapter = fw_spec['_queueadapter']
    assert qadapter.q_name == 'test_q'
    assert qadapter['walltime'] == 6
    assert qadapter['nodes'] == 1
    assert qadapter['ntasks_per_node'] == 4
    assert qadapter['pre_rocket'] == pre_rocket


def test_output_structure(meta_model, model_kwargs):
    """test output_structure: it is an AMML Structure object"""
    inp = ("calc = Calculator emt ();"
           "h2o = Structure ((atoms: ((symbols: 'O', 'H', 'H'),"
           "(x: 0.0, 0.0, 0.0) [angstrom],"
           "(y: 0.0, 0.763239, -0.763239) [angstrom],"
           "(z: 0.119262, -0.477047, -0.477047) [angstrom])));"
           "p1 = Property energy ((calculator: calc), (structure: h2o));"
           "h2o_out = p1.output_structure;"
           "print(h2o_out)")
    prog = meta_model.model_from_str(inp, **model_kwargs)
    var_list = get_children_of_type('Variable', prog)
    out_struct_val = next(v for v in var_list if v.name == 'h2o_out').value
    assert isinstance(out_struct_val, AMMLStructure)
    ref = ("Structure ((atoms: ((symbols: 'O', 'H', 'H'), (x: 0.0, 0.0, 0.0) [angstrom],"
           " (y: 0.0, 0.763239, -0.763239) [angstrom], (z: 0.119262, -0.477047, -0.477047)"
           " [angstrom], (px: 0.0, 0.0, 0.0) [electron_volt ** 0.5 * unified_atomic_mass_unit"
           " ** 0.5], (py: 0.0, 0.0, 0.0) [electron_volt ** 0.5 * unified_atomic_mass_unit **"
           " 0.5], (pz: 0.0, 0.0, 0.0) [electron_volt ** 0.5 * unified_atomic_mass_unit **"
           " 0.5], (masses: 15.999, 1.008, 1.008) [unified_atomic_mass_unit], (tags: 0, 0, 0)))"
           ", (cell: [[0.0, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0]]) [angstrom],"
           " (pbc: [false, false, false]))")
    assert prog.value == ref


def test_rdf_many_to_many(meta_model, model_kwargs):
    """test rdf algorithm in many-to-many relationship with structure"""
    inp = ("h2o = Structure water ("
           "        (atoms: ((symbols: 'O', 'H', 'H'),"
           "                 (x: 0., 0., 0.) [nm],"
           "                 (y: 0., 0.763239, -0.763239) [angstrom],"
           "                 (z: 0.119262, -0.477047, -0.477047) [angstrom]"
           "                ),"
           "                ((symbols: 'O', 'H', 'H'),"
           "                 (x: 0., 0., 0.) [nm],"
           "                 (y: 0., 0.763239, -0.763239) [angstrom],"
           "                 (z: 0.119262, -0.477047, -0.477047) [angstrom]"
           "                )"
           "        ),"
           "        (cell: [4., 4., 4.] [angstrom], [4., 4., 4.][angstrom]),"
           "        (pbc: [true, true, true], [true, true, true])"
           ");"
           "algo_rdf = Algorithm RDF ((nbins: 2));"
           "prop_rdf = Property rdf, rdf_distance ((structure: h2o), (algorithm: algo_rdf));"
           "print(prop_rdf.rdf);"
           "print(prop_rdf.rdf_distance)")
    output = ("(rdf: [7.214905040899412, 0.5153503600642437], [7.214905040899412,"
              " 0.5153503600642437])\n(rdf_distance: [0.49, 1.47], [0.49, 1.47]) [angstrom]")
    prog = meta_model.model_from_str(inp, **model_kwargs)
    assert prog.value == output


def test_rdf_many_to_one(meta_model, model_kwargs):
    """test rdf algorithm in many-to-one relationship with structure"""
    inp = ("h2o = Structure water ("
           "        (atoms: ((symbols: 'O', 'H', 'H'),"
           "                 (x: 0., 0., 0.) [nm],"
           "                 (y: 0., 0.763239, -0.763239) [angstrom],"
           "                 (z: 0.119262, -0.477047, -0.477047) [angstrom]"
           "                ),"
           "                ((symbols: 'O', 'H', 'H'),"
           "                 (x: 0., 0., 0.) [nm],"
           "                 (y: 0., 0.763239, -0.763239) [angstrom],"
           "                 (z: 0.119262, -0.477047, -0.477047) [angstrom]"
           "                )"
           "        ),"
           "        (cell: [4., 4., 4.] [angstrom], [4., 4., 4.][angstrom]),"
           "        (pbc: [true, true, true], [true, true, true])"
           ");"
           "algo_rdf = Algorithm RDF, many_to_one ((nbins: 2));"
           "prop_rdf = Property rdf, rdf_distance ((structure: h2o), (algorithm: algo_rdf));"
           "print(prop_rdf.rdf);"
           "print(prop_rdf.rdf_distance)")
    output = ("(rdf: [7.214905040899412, 0.5153503600642437])\n(rdf_distance:"
              " [0.49, 1.47]) [angstrom]")
    prog = meta_model.model_from_str(inp, **model_kwargs)
    assert prog.value == output


def test_structure_intrinsic_properties(meta_model, model_kwargs):
    """test structure intrinsic properties"""
    inp = ("h2o = Structure H2O ("
           "        (atoms: ((symbols: 'O', 'H', 'H'),"
           "               (x: 6., 6.96504783, 5.87761163) [angstrom],"
           "               (y: 6., 5.87761163, 6.96504783) [angstrom],"
           "               (z: 6., 6.00000000, 6.00000000) [angstrom]"
           "              )"
           "        ),"
           "        (cell: [[12., 0., 0.], [0., 12., 0.], [0., 0., 12.]] [angstrom])"
           ");"
           "print(h2o.kinetic_energy);"
           "print(h2o.temperature);"
           "print(h2o.distance_matrix);"
           "print(h2o.chemical_formula);"
           "print(h2o.number_of_atoms);"
           "print(h2o.cell_volume);"
           "print(h2o.center_of_mass);"
           "print(h2o.radius_of_gyration);"
           "print(h2o.moments_of_inertia);"
           "print(h2o.angular_momentum)")
    ref = ("(kinetic_energy: 0.0) [electron_volt]\n"
           "(temperature: 0.0) [kelvin]\n"
           "(distance_matrix: [[0.0, 0.9727775836741742, 0.9727775836741742], "
           "[0.9727775836741742, 0.0, 1.5378670222554613], [0.9727775836741742,"
           " 1.5378670222554613, 0.0]]) [angstrom]\n"
           "(chemical_formula: 'H2O')\n"
           "(number_of_atoms: 3)\n"
           "(cell_volume: 1728.000000000001) [angstrom ** 3]\n"
           "(center_of_mass: [6.047149638394671, 6.047149638394671, 6.0]) [angstrom]\n"
           "(radius_of_gyration: 0.6878006359031348) [angstrom]\n"
           "(moments_of_inertia: [0.6356576901727511, 1.1919776289830035, "
           "1.8276353191557546]) [angstrom ** 2 * unified_atomic_mass_unit]\n"
           "(angular_momentum: [0.0, 0.0, 0.0]) [angstrom * electron_volt ** "
           "0.5 * unified_atomic_mass_unit ** 0.5]")
    prog = meta_model.model_from_str(inp, **model_kwargs)
    assert prog.value == ref


def test_structure_with_referenced_positions(meta_model, model_kwargs):
    """test structure with atoms table as tuple of references"""
    inp = ("epsilon_K = 119.8 [K]; kB = 1. [boltzmann_constant]; sigma = 3.405 [angstrom];"
           "h = sigma * 2**(1/2) / 2; x = map((x: x*h), (x: 0., 1., 1., 0.));"
           "y = map((y: y*h), (y: 0., 1., 0., 1.)); z = map((z: z*h), (z: 0., 0., 1., 1.));"
           "symbols = (symbols: 'Ar', 'Ar', 'Ar', 'Ar');"
           "calc = Calculator lj ((sigma: sigma) , (epsilon: epsilon_K*kB));"
           "struct = Structure fcc_Ar4 ("
           "     (atoms: Table (symbols, x, y, z)),"
           "     (pbc: [true, true, true]),"
           "     (cell: [[4.82, 0., 0.], [0., 4.82, 0.], [0., 0., 4.82]] [angstrom]));"
           "prop = Property energy, forces ((calculator: calc), (structure: struct));"
           "print(prop.structure.atoms[0].x)")
    ref = "(x: 0.0, 2.4076985899401944, 2.4076985899401944, 0.0) [angstrom]"
    assert meta_model.model_from_str(inp, **model_kwargs).value == ref


def test_structure_with_momenta(meta_model, model_kwargs):
    """test a structure with momenta"""
    inp = ("epsilon_K = 119.8 [K]; kB = 1. [boltzmann_constant]; sigma = 3.405 [angstrom];"
           "h = sigma * 2**(1/2) / 2; x = map((x: x*h), (x: 0., 1., 1., 0.));"
           "y = map((y: y*h), (y: 0., 1., 0., 1.)); z = map((z: z*h), (z: 0., 0., 1., 1.));"
           "symbols = (symbols: 'Ar', 'Ar', 'Ar', 'Ar');"
           "calc = Calculator lj ((sigma: sigma) , (epsilon: epsilon_K*kB));"
           "struct = Structure fcc_Ar4 ("
           "          (atoms: ("
           "            (symbols: 'Ar', 'Ar', 'Ar', 'Ar'),"
           "            (x: 0., 2.41, 2.41, 0.) [angstrom],"
           "            (y: 0., 2.41, 0., 2.41) [angstrom],"
           "            (z: 0., 0., 2.41, 2.41) [angstrom],"
           "            (px: 0.0, 0.0, 0.0, 0.0) [eV ** 0.5 * amu ** 0.5],"
           "            (py: 0.0, 0.0, 0.0, 0.0) [eV ** 0.5 * amu ** 0.5],"
           "            (pz: 0.0, 0.0, 0.0, 0.0) [eV ** 0.5 * amu ** 0.5])"
           "          ),"
           "     (pbc: [true, true, true]),"
           "     (cell: [[4.82, 0., 0.], [0., 4.82, 0.], [0., 0., 4.82]] [angstrom]));"
           "prop = Property energy, forces ((calculator: calc), (structure: struct));"
           "print(prop.structure.atoms[0].px)")
    ref = "(px: 0.0, 0.0, 0.0, 0.0) [electron_volt ** 0.5 * unified_atomic_mass_unit ** 0.5]"
    assert meta_model.model_from_str(inp, **model_kwargs).value == ref
