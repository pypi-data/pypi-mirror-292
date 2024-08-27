import matplotlib
matplotlib.use("Agg")

import numpy as np
from ase import Atoms
from ase.io import read
from ase.optimize import BFGS

from agox import AGOX
from agox.acquisitors import MetaInformationAcquisitor
from agox.collectors import ParallelTemperingCollector
from agox.databases import Database
from agox.environments import Environment
from agox.evaluators import LocalOptimizationEvaluator
from agox.samplers import ParallelTemperingSampler
from agox.postprocessors import ParallelRelaxPostprocess

from agox.models.descriptors.fingerprint import Fingerprint
from agox.models.GPR.kernels import RBF, Constant as C, Noise
from agox.models.GPR import GPR
from agox.models.GPR.priors import Repulsive

seed = 42
database_index = 0

sample_size = 10
rattle_amplitudes = np.linspace(0.1, 5, sample_size)

################################################################################
# Calculator
##############################################################################

from ase.calculators.emt import EMT
calc = EMT()

##############################################################################
# System & general settings:
##############################################################################

db_path = "db{}.db".format(database_index)
database = Database(filename=db_path, order=6)

template = Atoms("", cell=np.eye(3) * 12)
confinement_cell = np.eye(3) * 6
confinement_corner = np.array([3, 3, 3])
environment = Environment(
    template=template,
    symbols="Au12Ni2",
    confinement_cell=confinement_cell,
    confinement_corner=confinement_corner,
)

##############################################################################
# Search Settings:
##############################################################################

# Setup a ML model.
descriptor = Fingerprint(environment=environment)
beta = 0.01
k0 = C(beta, (beta, beta)) * RBF()
k1 = C(1 - beta, (1 - beta, 1 - beta)) * RBF()
kernel = C(5000, (1, 1e5)) * (k0 + k1) + Noise(0.01, (0.01, 0.01))
model = GPR(descriptor=descriptor, kernel=kernel, database=database, prior=Repulsive())

sampler = ParallelTemperingSampler(
    t_min=0.02, t_max=2, swap="down", sample_size=sample_size, order=3, verbose=True,
    model=model)

random_generator_kwargs = dict(contiguous=True)

collector = ParallelTemperingCollector.from_sampler(
    sampler, environment, rattle_amplitudes, random_generator_kwargs=random_generator_kwargs, dynamic=False)

relaxer = ParallelRelaxPostprocess(
    model=model,
    constraints=environment.get_constraints(),
    optimizer_run_kwargs={"steps": 5, "fmax": 0.1}, 
    start_relax=0,
    optimizer=BFGS,
    order=2,
)

# Each iteration the lowest temperature walker/replica will be evaluated.
# Skip chance can be used to skip evaluations with some probability.
acquisitor = MetaInformationAcquisitor(
    meta_key="walker_index", skip_chance=0.0, order=4
)

evaluator = LocalOptimizationEvaluator(
    calc,
    number_to_evaluate=1,
    optimizer_kwargs={"logfile": None},
    optimizer_run_kwargs={"fmax": 0.05, "steps": 0},
    constraints=environment.get_constraints(),
    order=5,
)

agox = AGOX(
    collector,
    relaxer,
    sampler,
    acquisitor,
    evaluator,
    database,
    seed=seed,
)

# ##############################################################################
# # Lets get the show running!
# ##############################################################################

agox.run(N_iterations=10)
