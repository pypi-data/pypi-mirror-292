import numbers

import numpy as np

from fortoptim.optimizers.pso_utils import (fortran_mscpso_inertia,
                                            mscpso_inertia, update_pbest_gbest)
from fortoptim.problems import Ackley


class TestMCPSOUtils:
    def test_fortran_mcpso_intertia(self):
        current_iter = 100
        max_iter = 1000
        w_min = 0.4
        w_max = 0.9
        f_min = 1
        f_avg = 10

        f = np.array([10, 7, 1]).reshape(-1, 1)
        w = mscpso_inertia(current_iter, max_iter, w_min, w_max, f, f_min, f_avg)
        w_fortran = fortran_mscpso_inertia(
            current_iter, max_iter, w_min, w_max, f, f_min, f_avg
        )

        assert np.allclose(w, w_fortran)

    def test_mcpso_intertia(self):
        current_iter = 100
        max_iter = 1000
        w_min = 0.4
        w_max = 0.9
        f_min = 1
        f_avg = 10

        f = np.array([10, 7, 1]).reshape(-1, 1)
        w = mscpso_inertia(current_iter, max_iter, w_min, w_max, f, f_min, f_avg)
        assert np.isclose(w[0], w_max)

        f = 7
        assert np.isclose(
            w[1], w_min + (f - f_min) * (w_max - w_min) / (f_avg / 2 - f_min)
        )

        f = 1
        assert np.isclose(w[2], w_max - current_iter * (w_max - w_min) / max_iter)

        assert w.shape == (3, 1)

    def test_update_pbest_gbest(self):

        problem = Ackley(dim=2)

        sub_swarm = np.random.uniform(size=(4, 5, 2))

        sub_swarm_f = np.empty((4, 5, 1))
        sub_swarm_f_pbest = np.array([np.inf] * 4)
        sub_swarm_pbest = np.empty((4, 2))

        swarm_gbest = None
        swarm_f_gbest = np.inf
        swarm_f_avg = None

        # run the first time to set value of same variables
        swarm_gbest, swarm_f_gbest, swarm_f_avg = update_pbest_gbest(
            problem,
            sub_swarm,
            sub_swarm_f,
            sub_swarm_f_pbest,
            sub_swarm_pbest,
            swarm_gbest,
            swarm_f_gbest,
        )

        print(swarm_f_gbest)

        assert swarm_gbest.shape == (1, 2)
        assert isinstance(swarm_f_gbest, numbers.Number)
        assert isinstance(swarm_f_avg, numbers.Number)

        for i in range(4):
            assert np.allclose(sub_swarm_f[i], problem.get_values(sub_swarm[i]))

        assert np.all(~np.isinf(sub_swarm_f_pbest)) and sub_swarm_f_pbest.shape == (4,)
        assert np.all(~np.isinf(sub_swarm_pbest)) and sub_swarm_pbest.shape == (4, 2)
        assert swarm_gbest.shape == (1, 2)
        assert isinstance(swarm_f_gbest, numbers.Number)

        # simulate evolution
        for i in range(5):
            sub_swarm = np.random.uniform(size=(4, 5, 2))

            # create variables to be able to compare outputs
            sub_swarm_f_tmp = []
            for ii in range(4):
                sub_swarm_f_tmp.append(
                    problem.get_values(sub_swarm[ii]).reshape(1, 5, 1)
                )
            sub_swarm_f_tmp = np.concatenate(sub_swarm_f_tmp, axis=0)

            sub_swarm_f_pbest_tmp = np.asarray(sub_swarm_f_pbest)
            sub_swarm_pbest_tmp = np.asarray(sub_swarm_pbest)
            swarm_gbest_tmp = np.asarray(swarm_gbest)
            swarm_f_gbest_tmp = np.asarray(swarm_f_gbest)

            #
            swarm_gbest, swarm_f_gbest, swarm_f_avg = update_pbest_gbest(
                problem,
                sub_swarm,
                sub_swarm_f,
                sub_swarm_f_pbest,
                sub_swarm_pbest,
                swarm_gbest,
                swarm_f_gbest,
            )

            # tests
            assert np.allclose(sub_swarm_f, sub_swarm_f_tmp)
            assert np.all(sub_swarm_f_pbest <= sub_swarm_f_pbest_tmp)
            assert np.all(
                problem.get_values(sub_swarm_pbest)
                <= problem.get_values(sub_swarm_pbest_tmp)
            )
            assert problem.get_values(swarm_gbest) <= problem.get_values(
                swarm_gbest_tmp
            )
            assert swarm_f_gbest <= swarm_f_gbest_tmp
