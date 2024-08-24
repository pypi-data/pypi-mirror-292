from atomistics.calculators.lammps import (
    get_potential_dataframe,
)
from pylammpsmpi import LammpsASELibrary

from pyiron_lammps.parallel import (
    calculate_elastic_constants_parallel as calculate_elastic_constants,
)
from pyiron_lammps.parallel import (
    calculate_energy_volume_curve_parallel as calculate_energy_volume_curve,
)
from pyiron_lammps.parallel import (
    optimize_structure_parallel as optimize_structure,
)

from . import _version

__all__ = [
    get_potential_dataframe,
    optimize_structure,
    calculate_elastic_constants,
    calculate_energy_volume_curve,
]


def get_lammps_engine(
    working_directory=None,
    cores=1,
    comm=None,
    logger=None,
    log_file=None,
    library=None,
    disable_log_file=True,
):
    return LammpsASELibrary(
        working_directory=working_directory,
        cores=cores,
        comm=comm,
        logger=logger,
        log_file=log_file,
        library=library,
        disable_log_file=disable_log_file,
    )


__version__ = _version.get_versions()["version"]
