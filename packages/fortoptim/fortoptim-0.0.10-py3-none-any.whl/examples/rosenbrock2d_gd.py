import numpy as np

from fortoptim.optimizers import GradientDescentOptimizer
from fortoptim.problems import Rosenbrock2D

problem = Rosenbrock2D()

optimizer = GradientDescentOptimizer(lr=1e-3, backend="fortran")

history = optimizer.minimize(problem, x0=np.array([[-0.5, -0.5]]), iterations=100)

x_min = np.array([[-2, -1]])
x_max = np.array([[2, 3]])
x_plot = (x_max - x_min) * np.random.uniform(size=(10000, 2)) + x_min

history.plot_loss_history(log=True, show=True)
