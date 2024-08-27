"""
definitions of ASE calculators, algorithms with their parameters with
types, units, default values and outputs with types, units and default values
"""
import pandas
from virtmat.language.utilities.units import ureg, calc_pars

# todos:
# 1. parameter name mappings, for example temperature_K -> temperature
# 2. mappings of task string -> parameter sets
# 3. move ase_p_df from amml.py: property names, names mapping, units conversion
spec = {
  'vasp': {
    'module': 'ase.calculators.vasp',
    'class': 'Vasp',
    'modulefile': {'name': 'vasp', 'verspec': '>=5.0.0'},
    'envvars': {'VASP_COMMAND': '"$DO_PARALLEL $VASP_MPI"'}
  },
  'turbomole': {
    'module': 'ase.calculators.turbomole',
    'class': 'Turbomole',
    'modulefile': {'name': 'turbomole', 'verspec': '>=7.0'}
  },
  'lj': {
    'module': 'ase.calculators.lj',
    'class': 'LennardJones'
  },
  'lennardjones': {
    'module': 'ase.calculators.lj',
    'class': 'LennardJones'
  },
  'emt': {
    'module': 'ase.calculators.emt',
    'class': 'EMT'
  },
  'BFGS': {
    'module': 'ase.optimize',
    'class': 'BFGS',
    'requires_dof': True,
    'params': {
      'steps': {
        'default': ureg.Quantity(100000000),
        'type': int,
        'units': 'dimensionless',
        'method': 'run',
      },
      'maxstep': {
        'default': ureg.Quantity(0.2, 'angstrom'),
        'type': float,
        'units': 'angstrom',
        'method': 'class',
      },
      'trajectory': {
        'default': None,
        'type': bool,
        'units': None,
        'method': 'class',
      },
      'logfile': {
        'default': None,
        'type': str,
        'units': None,
        'method': 'class',
      },
      'interval': {
        'default': ureg.Quantity(1),
        'type': int,
        'units': 'dimensionless',
        'method': 'attach',
      },
      'fmax': {
        'default': ureg.Quantity(0.05, 'eV / angstrom'),
        'type': float,
        'units': 'eV / angstrom',
        'method': 'run',
      },
      'alpha': {
        'default': ureg.Quantity(70.0, 'eV * angstrom ** (-2)'),
        'type': float,
        'units': 'eV * angstrom ** (-2)',
        'method': 'class',
      },
    }
  },
  'LBFGS': {
    'module': 'ase.optimize',
    'class': 'LBFGS',
    'requires_dof': True,
    'params': {
      'steps': {
        'default': ureg.Quantity(100000000),
        'type': int,
        'units': 'dimensionless',
        'method': 'run',
      },
      'maxstep': {
        'default': ureg.Quantity(0.2, 'angstrom'),
        'type': float,
        'units': 'angstrom',
        'method': 'class',
      },
      'trajectory': {
        'default': None,
        'type': bool,
        'units': None,
        'method': 'class',
      },
      'logfile': {
        'default': None,
        'type': str,
        'units': None,
        'method': 'class',
      },
      'interval': {
        'default': ureg.Quantity(1),
        'type': int,
        'units': 'dimensionless',
        'method': 'attach',
      },
      'fmax': {
        'default': ureg.Quantity(0.05, 'eV / angstrom'),
        'type': float,
        'units': 'eV / angstrom',
        'method': 'run',
      },
      'memory': {
        'default': ureg.Quantity(100),
        'type': int,
        'units': 'dimensionless',
        'method': 'class',
      },
      'damping': {
        'default': ureg.Quantity(1.0),
        'type': float,
        'units': 'dimensionless',
        'method': 'class',
      },
      'alpha': {
        'default': ureg.Quantity(70.0, 'eV * angstrom ** (-2)'),
        'type': float,
        'units': 'eV * angstrom ** (-2)',
        'method': 'class',
      },
    }
  },
  'LBFGSLineSearch': {
    'module': 'ase.optimize',
    'class': 'LBFGSLineSearch',
    'requires_dof': True,
    'params': {
      'steps': {
        'default': ureg.Quantity(100000000),
        'type': int,
        'units': 'dimensionless',
        'method': 'run',
      },
      'maxstep': {
        'default': ureg.Quantity(0.2, 'angstrom'),
        'type': float,
        'units': 'angstrom',
        'method': 'class',
      },
      'trajectory': {
        'default': None,
        'type': bool,
        'units': None,
        'method': 'class',
      },
      'logfile': {
        'default': None,
        'type': str,
        'units': None,
        'method': 'class',
      },
      'interval': {
        'default': ureg.Quantity(1),
        'type': int,
        'units': 'dimensionless',
        'method': 'attach',
      },
      'fmax': {
        'default': ureg.Quantity(0.05, 'eV / angstrom'),
        'type': float,
        'units': 'eV / angstrom',
        'method': 'run',
      },
      'memory': {
        'default': ureg.Quantity(100),
        'type': int,
        'units': 'dimensionless',
        'method': 'class',
      },
      'damping': {
        'default': ureg.Quantity(1.0),
        'type': float,
        'units': 'dimensionless',
        'method': 'class',
      },
      'alpha': {
        'default': ureg.Quantity(70.0, 'eV * angstrom ** (-2)'),
        'type': float,
        'units': 'eV * angstrom ** (-2)',
        'method': 'class',
      },
    }
  },
  'QuasiNewton': {
    'module': 'ase.optimize',
    'class': 'QuasiNewton',
    'requires_dof': True,
    'params': {
      'steps': {
        'default': ureg.Quantity(100000000),
        'type': int,
        'units': 'dimensionless',
        'method': 'run',
      },
      'maxstep': {
        'default': ureg.Quantity(0.2, 'angstrom'),
        'type': float,
        'units': 'angstrom',
        'method': 'class',
      },
      'trajectory': {
        'default': None,
        'type': bool,
        'units': None,
        'method': 'class',
      },
      'logfile': {
        'default': None,
        'type': str,
        'units': None,
        'method': 'class',
      },
      'interval': {
        'default': ureg.Quantity(1),
        'type': int,
        'units': 'dimensionless',
        'method': 'attach',
      },
      'fmax': {
        'default': ureg.Quantity(0.05, 'eV / angstrom'),
        'type': float,
        'units': 'eV / angstrom',
        'method': 'run',
      },
    }
  },
  'BFGSLineSearch': {
    'module': 'ase.optimize',
    'class': 'BFGSLineSearch',
    'requires_dof': True,
    'params': {
      'steps': {
        'default': ureg.Quantity(100000000),
        'type': int,
        'units': 'dimensionless',
        'method': 'run',
      },
      'maxstep': {
        'default': ureg.Quantity(0.2, 'angstrom'),
        'type': float,
        'units': 'angstrom',
        'method': 'class',
      },
      'trajectory': {
        'default': None,
        'type': bool,
        'units': None,
        'method': 'class',
      },
      'logfile': {
        'default': None,
        'type': str,
        'units': None,
        'method': 'class',
      },
      'interval': {
        'default': ureg.Quantity(1),
        'type': int,
        'units': 'dimensionless',
        'method': 'attach',
      },
      'fmax': {
        'default': ureg.Quantity(0.05, 'eV / angstrom'),
        'type': float,
        'units': 'eV / angstrom',
        'method': 'run',
      },
    }
  },
  'GPMin': {
    'module': 'ase.optimize',
    'class': 'GPMin',
    'requires_dof': True,
    'params': {
      'steps': {
        'default': ureg.Quantity(100000000),
        'type': int,
        'units': 'dimensionless',
        'method': 'class',
      },
      'trajectory': {
        'default': None,
        'type': bool,
        'units': None,
        'method': 'class',
      },
      'logfile': {
        'default': None,
        'type': str,
        'units': None,
        'method': 'class',
      },
      'interval': {
        'default': ureg.Quantity(1),
        'type': int,
        'units': 'dimensionless',
        'method': 'attach',
      },
      'fmax': {
        'default': ureg.Quantity(0.05, 'eV / angstrom'),
        'type': float,
        'units': 'eV / angstrom',
        'method': 'run',
      },
      'prior': {
        'default': None,
        'type': object,
        'units': None,
        'method': 'class',
      },
      'kernel': {
        'default': None,
        'type': object,
        'units': None,
        'method': 'class',
      },
      'update_prior_strategy': {
        'default': 'maximum',
        'type': str,
        'units': None,
        'method': 'class',
      },
      'update_hyperparams': {
        'default': False,
        'type': bool,
        'units': None,
        'method': 'class',
      },
      'noise': {
        'default': ureg.Quantity(0.005),
        'type': float,
        'units': 'dimensionless',
        'method': 'class',
      },
      'weight': {
        'default': ureg.Quantity(1.0),
        'type': float,
        'units': 'dimensionless',
        'method': 'class',
      },
      'scale': {
        'default': ureg.Quantity(0.4),
        'type': float,
        'units': 'dimensionless',
        'method': 'class',
      },
    }
  },
  'FIRE': {
    'module': 'ase.optimize',
    'class': 'FIRE',
    'requires_dof': True,
    'params': {
      'steps': {
        'default': ureg.Quantity(100000000),
        'type': int,
        'units': 'dimensionless',
        'method': 'run',
      },
      'maxstep': {
        'default': ureg.Quantity(0.2, 'angstrom'),
        'type': float,
        'units': 'angstrom',
        'method': 'class',
      },
      'trajectory': {
        'default': None,
        'type': bool,
        'units': None,
        'method': 'class',
      },
      'logfile': {
        'default': None,
        'type': str,
        'units': None,
        'method': 'class',
      },
      'interval': {
        'default': ureg.Quantity(1),
        'type': int,
        'units': 'dimensionless',
        'method': 'attach',
      },
      'fmax': {
        'default': ureg.Quantity(0.05, 'eV / angstrom'),
        'type': float,
        'units': 'eV / angstrom',
        'method': 'run',
      },
      'dt': {
        'default': ureg.Quantity(0.1, 'angstrom * (amu / eV ) ** (1/2)'),
        'type': float,
        'units': 'angstrom * (amu / eV ) ** (1/2)',
        'method': 'class',
      },
      'dtmax': {
        'default': ureg.Quantity(1.0, 'angstrom * (amu / eV ) ** (1/2)'),
        'type': float,
        'units': 'angstrom * (amu / eV ) ** (1/2)',
        'method': 'class',
      },
      'downhill_check': {
        'default': False,
        'type': bool,
        'units': None,
        'method': 'class',
      },
    }
  },  # nb: 8 non-documented init parameters in FIRE: no explanation/no units
  'MDMin': {
    'module': 'ase.optimize',
    'class': 'MDMin',
    'requires_dof': True,
    'params': {
      'steps': {
        'default': ureg.Quantity(100000000),
        'type': int,
        'units': 'dimensionless',
        'method': 'run',
      },
      'maxstep': {
        'default': ureg.Quantity(0.2, 'angstrom'),
        'type': float,
        'units': 'angstrom',
        'method': 'class',
      },
      'trajectory': {
        'default': None,
        'type': bool,
        'units': None,
        'method': 'class',
      },
      'logfile': {
        'default': None,
        'type': str,
        'units': None,
        'method': 'class',
      },
      'interval': {
        'default': ureg.Quantity(1),
        'type': int,
        'units': 'dimensionless',
        'method': 'attach',
      },
      'fmax': {
        'default': ureg.Quantity(0.05, 'eV / angstrom'),
        'type': float,
        'units': 'eV / angstrom',
        'method': 'run',
      },
      'dt': {
        'default': ureg.Quantity(0.2, 'angstrom * (amu / eV ) ** (1/2)'),
        'type': float,
        'units': 'angstrom * (amu / eV ) ** (1/2)',
        'method': 'class',
      },
    }
  },
  'RMSD': {
    'module': 'virtmat.language.utilities.amml',
    'class': 'RMSD',
    'requires_dof': True,
    'params': {
      'reference': {
        'type': object,
        'units': None,
        'method': 'run'
      },
      'adjust': {
        'default': True,
        'type': bool,
        'units': None,
        'method': 'run'
      },
    }
  },
  'RDF': {
    'module': 'virtmat.language.utilities.amml',
    'class': 'RDF',
    'requires_dof': False,
    'params': {
      'rmax': {
        'default': None,
        'type': float,
        'units': 'angstrom',
        'method': 'run'
      },
      'nbins': {
        'default': ureg.Quantity(40),
        'type': int,
        'units': 'dimensionless',
        'method': 'run'
      },
      'neighborlist': {
        'default': None,
        'type': object,
        'units': None,
        'method': 'run'
      },
      'neighborlist_pars': {
        'default': pandas.DataFrame(),
        'type': dict,
        'units': None,
        'method': 'run'
      },
      'elements': {
        'default': None,
        'type': str,
        'units': None,
        'method': 'run'
      }
    }
  },
  'VelocityVerlet': {
    'module': 'ase.md.verlet',
    'class': 'VelocityVerlet',
    'requires_dof': True,
    'params': {
      'steps': {
        'default': ureg.Quantity(50),
        'type': int,
        'units': 'dimensionless',
        'method': 'run',
      },
      'logfile': {
        'default': None,
        'type': str,
        'units': None,
        'method': 'class',
      },
      'trajectory': {
        'default': None,
        'type': str,
        'units': None,
        'method': 'class',
      },
      'interval': {
        'default': ureg.Quantity(1),
        'type': int,
        'units': 'dimensionless',
        'method': 'attach',
      },
      'timestep': {
        'type': float,
        'units': 'angstrom * (amu / eV ) ** (1/2)',
        'method': 'class',
      },
    }
  },
  'Langevin': {
    'module': 'ase.md.langevin',
    'class': 'Langevin',
    'requires_dof': True,
    'params': {
      'steps': {
        'default': ureg.Quantity(50),
        'type': int,
        'units': 'dimensionless',
        'method': 'run',
      },
      'logfile': {
        'default': None,
        'type': str,
        'units': None,
        'method': 'class',
      },
      'trajectory': {
        'default': None,
        'type': str,
        'units': None,
        'method': 'class',
      },
      'interval': {
        'default': ureg.Quantity(1),
        'type': int,
        'units': 'dimensionless',
        'method': 'attach',
      },
      'timestep': {
        'type': float,
        'units': 'angstrom * (amu / eV ) ** (1/2)',
        'method': 'class',
      },
      'temperature_K': {
        'type': float,
        'units': 'K',
        'method': 'class',
      },
      'friction': {
        'type': float,
        'units': 'angstrom ** (-1) * (amu / eV ) ** (-1/2)',
        'method': 'class',
      },
      'fixcm': {
        'default': True,
        'type': bool,
        'units': None,
        'method': 'class',
      },
    }
  },
  'NPT': {
    'module': 'ase.md.npt',
    'class': 'NPT',
    'requires_dof': True,
    'params': {
      'steps': {
        'default': ureg.Quantity(50),
        'type': int,
        'units': 'dimensionless',
        'method': 'run',
      },
      'logfile': {
        'default': None,
        'type': str,
        'units': None,
        'method': 'class',
      },
      'trajectory': {
        'default': None,
        'type': str,
        'units': None,
        'method': 'class',
      },
      'interval': {
        'default': ureg.Quantity(1),
        'type': int,
        'units': 'dimensionless',
        'method': 'attach',
      },
      'timestep': {
        'type': float,
        'units': 'angstrom * (amu / eV ) ** (1/2)',
        'method': 'class',
      },
      'temperature_K': {
        'type': float,
        'units': 'K',
        'method': 'class',
      },
      'externalstress': {
        'type': float,
        'units': 'eV / (angstrom ** 3)',
        'method': 'class',
      },
      'ttime': {
        'type': float,
        'units': 'angstrom * (amu / eV ) ** (1/2)',
        'method': 'class',
      },
      'pfactor': {
        'type': float,
        'units': 'amu  / angstrom',
        'method': 'class',
      },
    }
  },
  'Andersen': {
    'module': 'ase.md.andersen',
    'class': 'Andersen',
    'requires_dof': True,
    'params': {
      'steps': {
        'default': ureg.Quantity(50),
        'type': int,
        'units': 'dimensionless',
        'method': 'run',
      },
      'logfile': {
        'default': None,
        'type': str,
        'units': None,
        'method': 'class',
      },
      'trajectory': {
        'default': None,
        'type': str,
        'units': None,
        'method': 'class',
      },
      'interval': {
        'default': ureg.Quantity(1),
        'type': int,
        'units': 'dimensionless',
        'method': 'attach',
      },
      'timestep': {
        'type': float,
        'units': 'angstrom * (amu / eV ) ** (1/2)',
        'method': 'class',
      },
      'temperature_K': {
        'type': float,
        'units': 'K',
        'method': 'class',
      },
      'andersen_prob': {
        'type': float,
        'units': 'dimensionless',
        'method': 'class',
      },
      'fixcm': {
        'default': True,
        'type': bool,
        'units': None,
        'method': 'class',
      },
    }
  },
  'NVTBerendsen': {
    'module': 'ase.md.nvtberendsen',
    'class': 'NVTBerendsen',
    'requires_dof': True,
    'params': {
      'steps': {
        'default': ureg.Quantity(50),
        'type': int,
        'units': 'dimensionless',
        'method': 'run',
      },
      'logfile': {
        'default': None,
        'type': str,
        'units': None,
        'method': 'class',
      },
      'trajectory': {
        'default': None,
        'type': str,
        'units': None,
        'method': 'class',
      },
      'interval': {
        'default': ureg.Quantity(1),
        'type': int,
        'units': 'dimensionless',
        'method': 'attach',
      },
      'timestep': {
        'type': float,
        'units': 'angstrom * (amu / eV ) ** (1/2)',
        'method': 'class',
      },
      'temperature_K': {
        'type': float,
        'units': 'K',
        'method': 'class',
      },
      'taut': {
        'type': float,
        'units': 'angstrom * (amu / eV ) ** (1/2)',
        'method': 'class',
      },
      'fixcm': {
        'default': True,
        'type': bool,
        'units': None,
        'method': 'class',
      },
    }
  },
  'NPTBerendsen': {
    'module': 'ase.md.nptberendsen',
    'class': 'NPTBerendsen',
    'requires_dof': True,
    'params': {
      'steps': {
        'default': ureg.Quantity(50),
        'type': int,
        'units': 'dimensionless',
        'method': 'run',
      },
      'logfile': {
        'default': None,
        'type': str,
        'units': None,
        'method': 'class',
      },
      'trajectory': {
        'default': None,
        'type': str,
        'units': None,
        'method': 'class',
      },
      'interval': {
        'default': ureg.Quantity(1),
        'type': int,
        'units': 'dimensionless',
        'method': 'attach',
      },
      'timestep': {
        'type': float,
        'units': 'angstrom * (amu / eV ) ** (1/2)',
        'method': 'class',
      },
      'temperature_K': {
        'type': float,
        'units': 'K',
        'method': 'class',
      },
      'pressure_au': {
        'type': float,
        'units': 'eV / (angstrom ** 3)',
        'method': 'class',
      },
      'taut': {
        'default': ureg.Quantity(0.5, 'ps'),
        'type': float,
        'units': 'angstrom * (amu / eV ) ** (1/2)',
        'method': 'class',
      },
      'taup': {
        'default': ureg.Quantity(1.0, 'ps'),
        'type': float,
        'units': 'angstrom * (amu / eV ) ** (1/2)',
        'method': 'class',
      },
      'compressibility_au': {
        'type': float,
        'units': 'angstrom ** 3 / eV',
        'method': 'class',
      },
      'fixcm': {
        'default': True,
        'type': bool,
        'units': None,
        'method': 'class',
      },
    }
  },
}

for calc in ('vasp', 'turbomole', 'lj', 'lennardjones', 'emt'):
    spec[calc]['params'] = {k: {'units': v} for k, v in calc_pars[calc].items()}

par_units = {c: {k: v['units'] for k, v in u['params'].items()} for c, u in spec.items()}
