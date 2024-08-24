"""Module containing implementation of PSO algorithms
Only contain MCPSO atm
"""

import copy
import numbers

import numpy as np

from FortOptim.history_manager import OptimizerHistory
from FortOptim.optimizers.pso_utils import (
    mscpso_inertia,
    fortran_mscpso_inertia,
    update_pbest_gbest,
    fortran_update_velocity,
    update_velocity,
    fortran_update_velocity_3,
    update_velocity_3,
)


class MultiSwarmCooperativePSO:
    """Implementation from the paper:
    A Multi-Swarm Self-Adaptive and Cooperative Particle Swarm Optimization,
    Jiuzhong Zhang, Xueming Ding
    """

    def __init__(
        self,
        c12=(1.7, 2.05),
        impact_factors=(1 / 6, 1 / 3, 1 / 2),
        inertia_parameters={"name": "MCPSO", "w_min": 0.4, "w_max": 0.9},
        velocity_clamping_factor=0.2,
        topology="star",
        eps=1e-6,
        backend="numpy",
    ):
        self.eps = eps
        self.c1 = c12[0]
        self.c2 = c12[1]

        self.a1 = impact_factors[0]
        self.a2 = impact_factors[1]
        self.a3 = impact_factors[2]

        self.backend = backend
        if backend == "numpy":
            self.mscpso_inertia = mscpso_inertia
            self.update_velocity = update_velocity
            self.update_velocity_3 = update_velocity_3
        if backend == "fortran":
            self.mscpso_inertia = fortran_mscpso_inertia
            self.update_velocity = fortran_update_velocity
            self.update_velocity_3 = fortran_update_velocity_3

        if isinstance(velocity_clamping_factor, numbers.Number):
            self.velocity_clamping = True
            self.velocity_clamping_factor = velocity_clamping_factor
        else:
            self.velocity_clamping = False

        self.w_min = inertia_parameters["w_min"]
        self.w_max = inertia_parameters["w_max"]

        if topology != "star":
            raise NotImplementedError("Topology other than star not impemented.")

    def minimize(
        self,
        problem,
        sub_swarm,
        sub_swarm_velocity,
        max_iter=None,
        max_feval=1000,
        seed=None,
    ):

        # get attributes
        c1 = self.c1
        c2 = self.c2
        a1 = self.a1
        a2 = self.a2
        a3 = self.a3
        eps = self.eps
        mscpso_inertia = self.mscpso_inertia
        velocity_clamping = self.velocity_clamping
        dim = problem.dim
        update_velocity = self.update_velocity

        constraints = problem.constraints
        problem_constrained = problem.constraints is not None

        w_min = self.w_min
        w_max = self.w_max

        if problem_constrained:
            lower_domain_bound = np.array([constraint[0] for constraint in constraints])
            upper_domain_bound = np.array([constraint[1] for constraint in constraints])

        if velocity_clamping:
            constaints = problem.constraints
            dx = np.array(
                [[constraint[1] - constraint[0] for constraint in constaints]]
            )
            velocity_max = self.velocity_clamping_factor * dx

        # swarm size
        n_sub_swarm = sub_swarm[0].shape[0]
        n = 4 * n_sub_swarm

        # number of iterations
        if max_iter is None:
            max_iter = max_feval // n

        # reshape for simpler data structure
        sub_swarm_tmp = []
        sub_swarm_velocity_tmp = []
        for i in range(4):
            new_shape = (1, *sub_swarm[i].shape)
            sub_swarm_tmp.append(sub_swarm[i].reshape(new_shape))
            sub_swarm_velocity_tmp.append(sub_swarm_velocity[i].reshape(new_shape))
        sub_swarm = np.concatenate(sub_swarm_tmp, axis=0)
        sub_swarm_velocity = np.concatenate(sub_swarm_velocity_tmp, axis=0)

        # compute pbest and gbest
        sub_swarm_f = np.empty((4, n_sub_swarm, 1))
        sub_swarm_f_pbest = np.array([np.inf] * 4)
        sub_swarm_pbest = np.empty((4, 1, dim))

        swarm_gbest = None
        swarm_f_gbest = np.inf
        swarm_f_avg = None

        swarm_gbest, swarm_f_gbest, swarm_f_avg = update_pbest_gbest(
            problem,
            sub_swarm,
            sub_swarm_f,
            sub_swarm_f_pbest,
            sub_swarm_pbest,
            swarm_gbest,
            swarm_f_gbest,
        )

        # optimization loop
        if seed is not None:
            np.random.seed(seed)

        history = OptimizerHistory()
        for i in range(max_iter):

            # -----------------------------
            # compute velocities
            # -----------------------------
            # basic sub-swarms 1 and 2
            for j in range(2):

                w = mscpso_inertia(
                    i,
                    max_iter,
                    w_min,
                    w_max,
                    sub_swarm_f[j],
                    swarm_f_gbest,
                    swarm_f_avg,
                )

                sub_swarm_velocity[j] = update_velocity(
                    sub_swarm_velocity[j],
                    sub_swarm[j],
                    w,
                    c1,
                    c2,
                    sub_swarm_pbest[j],
                    swarm_gbest,
                    seed=np.random.randint(low=0, high=10000),
                )

            # adaptative swarm 3
            w = mscpso_inertia(
                i,
                max_iter,
                w_min,
                w_max,
                sub_swarm_f[2],
                swarm_f_gbest,
                swarm_f_avg,
            )

            gamma1 = sub_swarm_f[0]
            gamma2 = sub_swarm_f[1]

            sub_swarm_velocity[2] = update_velocity_3(
                sub_swarm_velocity[2],
                sub_swarm_velocity[0],
                sub_swarm_velocity[1],
                gamma1,
                gamma2,
                sub_swarm[2],
                w,
                c1,
                c2,
                sub_swarm_pbest[2],
                swarm_gbest,
                eps=eps,
                seed=np.random.randint(low=0, high=10000),
            )

            # gamma = gamma1 + gamma2
            # sub_swarm_velocity[2] = (
            #     w
            #     * (
            #         sub_swarm_velocity[2]
            #         + gamma / (gamma1 + eps) * sub_swarm_velocity[0]
            #         + gamma / (gamma2 + eps) * sub_swarm_velocity[1]
            #     )
            #     + c1
            #     * np.random.uniform(size=(n_sub_swarm, 1))
            #     * (sub_swarm_pbest[2] - sub_swarm[2])
            #     + c2
            #     * np.random.uniform(size=(n_sub_swarm, 1))
            #     * (swarm_gbest - sub_swarm[2])
            # )

            # sub swarm 4
            sub_swarm_velocity[3] = (
                sub_swarm_velocity[0] + sub_swarm_velocity[1] - sub_swarm_velocity[2]
            )

            # velocity clamping for every component
            if velocity_clamping:
                sub_swarm_velocity = np.where(
                    np.abs(sub_swarm_velocity) > velocity_max,
                    0.0,
                    sub_swarm_velocity,
                )

            # -----------------------------
            # update positions
            # -----------------------------
            for j in range(3):
                sub_swarm[j] = sub_swarm[j] + sub_swarm_velocity[j]

            # sub swarm 4
            sub_swarm[3] = (
                a1 * sub_swarm[3]
                + a2 * sub_swarm_pbest[3]
                + a3 * swarm_gbest
                + sub_swarm_velocity[3]
            )

            # put points outside back on the counstraints
            if problem_constrained:
                # lower bound
                sub_swarm = np.maximum(sub_swarm, lower_domain_bound)
                # upper bound
                sub_swarm = np.minimum(sub_swarm, upper_domain_bound)

            # update pbest and gbest
            swarm_gbest, swarm_f_gbest, swarn_f_avg = update_pbest_gbest(
                problem,
                sub_swarm,
                sub_swarm_f,
                sub_swarm_f_pbest,
                sub_swarm_pbest,
                swarm_gbest,
                swarm_f_gbest,
            )

            # save gbest
            history.add(copy.deepcopy(swarm_gbest), swarm_f_gbest)

        # save last state
        sub_swarm = [sub_swarm[i] for i in range(4)]
        history.add_to_last_state_dict("sub swarm", sub_swarm)
        history.add_to_last_state_dict("sub swarm values", sub_swarm_f)

        return history
