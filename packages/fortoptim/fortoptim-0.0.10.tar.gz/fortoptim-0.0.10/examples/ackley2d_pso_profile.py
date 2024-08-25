import numpy as np
import cProfile, pstats

from fortoptim.optimizers.pso import MultiSwarmCooperativePSO
from fortoptim.problems import Ackley

SEED = 123
np.random.seed(SEED)

dim = 2
lower = -32
upper = 32
constraints = [np.array([lower, upper])] * dim
problem = Ackley(dim=dim, constraints=constraints)

# initial population and velocity
n = 6
sub_swarm = [np.random.uniform(size=(n, dim), low=lower, high=upper) for i in range(4)]
# sub_swarm_velocity = [np.random.uniform(size=(n, dim), high=0.8) for i in range(4)]
sub_swarm_velocity = [np.zeros(shape=(n, dim)) for i in range(4)]

# initialize optimizer with default parameters
opti = MultiSwarmCooperativePSO(eps=0.0, backend='fortran')

with cProfile.Profile() as profile:
    opti.minimize(problem, sub_swarm, sub_swarm_velocity, max_iter=10000)

results = pstats.Stats(profile)
results.sort_stats(pstats.SortKey.TIME)
results.dump_stats('ackley_fortran.prof')
