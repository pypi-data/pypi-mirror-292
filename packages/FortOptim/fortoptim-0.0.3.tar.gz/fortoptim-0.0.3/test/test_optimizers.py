import numpy as np

from FortOptim.optimizers import (GradientDescentOptimizer,
                                  MultiSwarmCooperativePSO)
from FortOptim.problems import Ackley, Rosenbrock2D


class TestOptimizers:

    def test_gradient_descent_on_rosenbrock_2d(self):
        """Test GradientDescentOptimizer on Rosenbrock2D problem"""
        problem = Rosenbrock2D()
        optimizer = GradientDescentOptimizer(lr=1e-3, backend="fortran")
        history = optimizer.minimize(
            problem, x0=np.array([[-0.5, -0.5]]), iterations=100
        )

        assert np.allclose(history.x_history[-1], np.array([[0.11320665, 0.00953239]]))

    def test_mscpso_on_ackley_2d(self):

        SEED = 123
        np.random.seed(SEED)

        dim = 2
        lower = -32
        upper = 32
        constraints = [np.array([lower, upper])] * dim
        problem = Ackley(dim=dim, constraints=constraints)

        # initial population and velocity
        n = 30
        sub_swarm = [
            np.random.uniform(size=(n, dim), low=lower, high=upper) for i in range(4)
        ]
        sub_swarm_velocity = [
            np.random.uniform(size=(n, dim), high=0.8) for i in range(4)
        ]

        # initialize optimizer with default parameters
        opti = MultiSwarmCooperativePSO(eps=0.0)

        history = opti.minimize(problem, sub_swarm, sub_swarm_velocity, max_iter=1000)
        x_best, f_best = history.get_best_solution()
        assert np.allclose(x_best, np.zeros_like(x_best))
