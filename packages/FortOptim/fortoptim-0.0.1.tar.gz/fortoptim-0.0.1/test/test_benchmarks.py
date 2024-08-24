"""Test module for every problems"""

import numpy as np
import pytest

from FortOptim.problems import Ackley
from FortOptim.problems import Beale
from FortOptim.problems import Booth
from FortOptim.problems import Rosenbrock2D
from FortOptim.problems import Sphere


@pytest.mark.skip(
    reason="This is a helper function that is not supposed to be called alone."
)
def test_problem(problem):
    """test every function of a problem"""

    x_sol, f_sol = problem.get_solution()
    assert np.all(problem.is_solution(x_sol))

    problem.get_solution()
    grad = problem.get_gradients(x_sol)
    assert np.allclose(grad, np.zeros(shape=(1, problem.dim)))


class TestBenchmarks:
    """Class to test every implemented test problem"""

    def test_rosenbrock2d(self):
        problem = Rosenbrock2D()
        test_problem(problem)

    def test_sphere(self):
        problem = Sphere(2)
        test_problem(problem)

    def test_ackley(self):
        problem = Ackley(dim=2)
        test_problem(problem)

    def test_beale(self):
        problem = Beale()
        test_problem(problem)

    def test_booth(self):
        problem = Booth()
        test_problem(problem)
