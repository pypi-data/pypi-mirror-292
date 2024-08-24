"""Module containing functions for PSO"""

import numpy as np

from FortOptim.src import (
    fortran_linear_inertia,
    fortran_mscpso_inertia,
    fortran_update_velocity,
    fortran_update_velocity_3,
)


def update_velocity_3(
    velocity3,
    velocity1,
    velocity2,
    gamma1,
    gamma2,
    sub_swarm,
    w,
    c1,
    c2,
    pbest,
    gbest,
    eps,
    seed,
):
    n_sub_swarm = sub_swarm.shape[0]

    gamma = gamma1 + gamma2
    velocity3 = (
        w
        * (
            velocity3
            + gamma / (gamma1 + eps) * velocity1
            + gamma / (gamma2 + eps) * velocity2
        )
        + c1 * np.random.uniform(size=(n_sub_swarm, 1)) * (pbest - sub_swarm)
        + c2 * np.random.uniform(size=(n_sub_swarm, 1)) * (gbest - sub_swarm)
    )

    return velocity3


def update_velocity(sub_swarm_velocity, sub_swarm, w, c1, c2, pbest, gbest, seed=None):
    n_sub_swarm = sub_swarm.shape[0]

    sub_swarm_velocity = (
        w * sub_swarm_velocity
        + c1 * np.random.uniform(size=(n_sub_swarm, 1)) * (pbest - sub_swarm)
        + c2 * np.random.uniform(size=(n_sub_swarm, 1)) * (gbest - sub_swarm)
    )

    return sub_swarm_velocity


def linear_inertia(current_iter, max_iter, w_min, w_max):
    return (w_max - w_min) * (max_iter - current_iter) / max_iter + w_min


def mscpso_inertia(current_iter, max_iter, w_min, w_max, f, f_min, f_avg):

    w_tmp = np.where(
        f >= f_avg / 2,
        w_min + (f - f_min) * (w_max - w_min) / (f_avg / 2 - f_min),
        linear_inertia(current_iter, max_iter, w_min, w_max),
    )

    w = np.where(f >= f_avg, w_max, w_tmp)
    return w


def update_pbest_gbest(
    problem,
    sub_swarm,
    sub_swarm_f,
    sub_swarm_f_pbest,
    sub_swarm_pbest,
    swarm_gbest,
    swarm_f_gbest,
):

    swarm_f_avg = 0.0

    for i in range(4):
        sub_swarm_f[i] = problem.get_values(sub_swarm[i])
        swarm_f_avg = swarm_f_avg + np.mean(sub_swarm_f[i], axis=0)[0]

        sub_swarm_current_f_pbest_i = np.min(sub_swarm_f[i], axis=0)[0]

        # update pbest
        if sub_swarm_current_f_pbest_i < sub_swarm_f_pbest[i]:
            sub_swarm_pbest[i] = np.asarray(
                sub_swarm[i, np.argmin(sub_swarm_f[i]), :]
            ).reshape(1, -1)
            sub_swarm_f_pbest[i] = sub_swarm_current_f_pbest_i

            # update gbest
            if swarm_f_gbest > sub_swarm_f_pbest[i]:
                swarm_f_gbest = sub_swarm_f_pbest[i]
                swarm_gbest = np.asarray(sub_swarm_pbest[i]).reshape(1, -1)
    return swarm_gbest, swarm_f_gbest, swarm_f_avg / 4.0
