import numpy as np

from fortoptim.optimizers.pso import MultiSwarmCooperativePSO
from fortoptim.problems import Ackley

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
opti = MultiSwarmCooperativePSO(eps=0.0)

history = opti.minimize(problem, sub_swarm, sub_swarm_velocity, max_iter=10000)

x_plot = np.random.uniform(size=(200000, dim), low=lower, high=upper)

x_best, f_best = history.get_best_solution()
print(f"The best solution is {x_best} obtained at {f_best}.")

history.plot_loss_history(log=True, show=True)
