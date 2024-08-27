"""checks / constraints for AMML objects"""
from textx import get_children_of_type
from virtmat.language.utilities.errors import raise_exception, StaticValueError
from virtmat.language.utilities.textx import get_reference

compat_calc = {
  'single point': ['energy', 'forces', 'dipole', 'stress', 'charges'],
  'local minimum': ['energy', 'forces', 'dipole', 'stress', 'charges', 'trajectory'],
  'global minimum': ['energy', 'forces', 'dipole', 'stress', 'charges', 'trajectory'],
  'transition state': ['energy', 'forces', 'dipole', 'stress', 'charges', 'trajectory'],
  'normal modes': ['vibrational_energies', 'energy_minimum', 'transition_state'],
  'micro-canonical': ['energy', 'forces', 'dipole', 'stress', 'charges', 'trajectory'],
  'canonical': ['energy', 'forces', 'dipole', 'stress', 'charges', 'trajectory'],
  'isothermal-isobaric': ['energy', 'forces', 'dipole', 'stress', 'charges', 'trajectory'],
  'grand-canonical': ['energy', 'forces', 'dipole', 'stress', 'charges', 'trajectory']
}

compat_algo = {
  'BFGSLineSearch': ['energy', 'forces', 'trajectory'],
  'BFGSClimbFixInternals': ['energy', 'forces', 'trajectory'],
  'BFGS': ['energy', 'forces', 'trajectory'],
  'LBFGSLineSearch': ['energy', 'forces', 'trajectory'],
  'LBFGS': ['energy', 'forces', 'trajectory'],
  'GPMin': ['energy', 'forces', 'trajectory'],
  'MDMin': ['energy', 'forces', 'trajectory'],
  'QuasiNewton': ['energy', 'forces', 'trajectory'],
  'FIRE': ['energy', 'forces', 'trajectory'],
  'VelocityVerlet': ['energy', 'forces', 'trajectory'],
  'Langevin': ['energy', 'forces', 'trajectory'],
  'Andersen': ['energy', 'forces', 'trajectory'],
  'NVTBerendsen': ['energy', 'forces', 'trajectory'],
  'NPTBerendsen': ['energy', 'forces', 'trajectory'],
  'NPT': ['energy', 'forces', 'trajectory'],
  'NEB': ['energy', 'forces', 'trajectory'],
  'Dimer': ['energy', 'forces', 'trajectory'],
  'BasinHopping': ['energy', 'trajectory'],
  'MinimaHopping': ['energy', 'trajectory'],
  'GA': ['energy', 'trajectory'],
  'RDF': ['rdf_distance', 'rdf'],
  'RMSD': ['rmsd']
}


def check_task_property_processor(model, _):
    """check compatibility of properties with calculator task"""
    for obj in get_children_of_type('AMMLProperty', model):
        task = get_reference(obj.calc).task if obj.calc else None
        algo = get_reference(obj.algo).name if obj.algo else None
        talgo = 'task \"' + str(task or '') + '\" or algo \"' + str(algo or '') + '\"'
        for name in obj.names:
            if (task or algo) and not ((task and name in compat_calc[task]) or
               (algo and name in compat_algo[algo])):
                msg = f'property \"{name}\" not available in {talgo}'
                raise_exception(obj, StaticValueError, msg)
