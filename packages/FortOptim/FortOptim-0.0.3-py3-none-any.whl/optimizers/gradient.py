"""Optimizer abstract base class"""

import numpy as np
import copy

from FortOptim.history_manager import OptimizerHistory
from FortOptim.src import fortran_apply_gradient


class GradientDescentOptimizer:

    def __init__(self, lr=1e-3, line_search=False, momentum=False, eps=1e-6, backend='numpy'):
        self.lr = lr
        self.line_search = line_search
        self.momentum = momentum
        self.eps = eps
        self.backend = backend

    def minimize(self, problem, x0, iterations):
        """optimization loop on the given problem"""
        lr = self.lr
        eps = self.eps
        x_old = np.asarray(x0)
        x = np.asarray(x0)
        backend = self.backend

        history = OptimizerHistory()

        f0 = problem.get_values(x0)
        history.add(x0, f0)

        for iteration in range(1, iterations + 1):

            # obtain gradient
            grad = problem.get_gradients(x_old)

            # apply gradient
            if backend=='numpy':
                x = x_old - lr * grad

            if backend=='fortran':
                #x = fortran_apply_gradient(x_old, grad, lr)
                x = fortran_apply_gradient(x_old, grad, lr)

            # save in history
            f = problem.get_values(x)
            history.add(x, f)

            # update previous iterate
            x_old = np.asarray(x)

            # check convergence
            converged = np.linalg.norm(grad) < eps
            if converged:
                break

        print(f"Converged: {converged}\nIterations: {iteration}")

        x_best, f_best = history.get_best_solution()
        print(f"Best solution: {x_best}\nBest value: {f_best}")
        return history
