"""Different History classes for each optimizer"""

import matplotlib
import matplotlib.pyplot as plt
import numpy as np


class OptimizerHistory:
    def __init__(self):
        self.x_history = []
        self.f_history = []
        self.last_state = {}

    def add_to_last_state_dict(self, name, value):
        self.last_state[name] = value

    def add(self, x, f):
        self.x_history.append(x)
        self.f_history.append(f)

    def get_best_solution(self):
        ind_min = self.f_history.index(min(self.f_history))
        return self.x_history[ind_min], self.f_history[ind_min]

    def plot_variable_trajectory(
        self,
        problem,
        x_plot=None,
        x_min=None,
        x_max=None,
        npts=1000,
        freq=100,
        log=True,
        plot_name=None,
        levels=100,
        xlim=None,
        ylim=None,
        show=False,
    ):
        if problem.dim != 2:
            raise NotImplementedError(
                "vizualization for parameter space dimension different than 2 not implemented."
            )

        if x_plot is None:
            x_plot = (x_max - x_min) * np.random.uniform(size=(npts, 2)) + x_min

        # plot trajectory of variables
        f = problem.get_values(x_plot).reshape(-1)
        if log:
            norm = matplotlib.colors.LogNorm()
        else:
            norm = None
        plt.tricontourf(x_plot[:, 0], x_plot[:, 1], f, norm=norm, levels=levels)

        x_trajectory = np.concatenate(self.x_history[::freq], axis=0)
        plt.plot(x_trajectory[:, 0], x_trajectory[:, 1], c="black", marker="x")

        # add test
        for i, x_ in enumerate(x_trajectory):
            plt.text(x_[0], x_[1], i)

        plt.colorbar()
        if xlim is not None:
            plt.xlim(xlim)
        if ylim is not None:
            plt.ylim(ylim)

        if show:
            plt.show()

        if plot_name is not None:
            plt.savefig(f"{plot_name}.png")

        plt.clf()

    def plot_loss_history(
        self,
        log=True,
        plot_name=False,
        show=False,
    ):
        # plot convergence wrt to iterations
        f_history = np.stack(self.f_history, axis=0).reshape(-1)
        plt.plot(f_history)

        plt.xlabel("iterations")
        plt.ylabel("loss value(s)")

        if log:
            plt.yscale("log")

        if show:
            plt.show()

        if plot_name is not None:
            plt.savefig(f"{plot_name}.png")

        plt.clf()
