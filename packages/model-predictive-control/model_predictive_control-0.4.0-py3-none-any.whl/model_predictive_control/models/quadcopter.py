from typing import Optional, Tuple, cast

import numpy as np

from .base import (
    BaseRobot,
    BaseRobotInputs,
    BaseRobotModel,
    BaseRobotParams,
    BaseRobotState,
)


class QuadcopterModelParams(BaseRobotParams):
    time_step: float
    mass: float
    inertia: Tuple[float, float, float]
    arm_length: float
    gravity: float = 9.81


class QuadcopterModelState(BaseRobotState):
    x: float
    y: float
    z: float
    phi: float  # roll
    theta: float  # pitch
    psi: float  # yaw
    vx: float
    vy: float
    vz: float
    omega_x: float
    omega_y: float
    omega_z: float

    def totuple(self) -> Tuple[float, ...]:
        return (
            self.x,
            self.y,
            self.z,
            self.phi,
            self.theta,
            self.psi,
            self.vx,
            self.vy,
            self.vz,
            self.omega_x,
            self.omega_y,
            self.omega_z,
        )

    @staticmethod
    def fromtuple(x: Tuple[float, ...]) -> "QuadcopterModelState":
        assert len(x) == 12
        return QuadcopterModelState(
            x=x[0],
            y=x[1],
            z=x[2],
            phi=x[3],
            theta=x[4],
            psi=x[5],
            vx=x[6],
            vy=x[7],
            vz=x[8],
            omega_x=x[9],
            omega_y=x[10],
            omega_z=x[11],
        )


class QuadcopterModelInputs(BaseRobotInputs):
    thrust: float
    torque_x: float
    torque_y: float
    torque_z: float

    def totuple(self) -> Tuple[float, float, float, float]:
        return (self.thrust, self.torque_x, self.torque_y, self.torque_z)

    @staticmethod
    def fromtuple(
        x: Tuple[float, float, float, float]
    ) -> "QuadcopterModelInputs":
        assert len(x) == 4
        return QuadcopterModelInputs(
            thrust=x[0], torque_x=x[1], torque_y=x[2], torque_z=x[3]
        )


def quadcopter_model(
    state: Tuple[float, ...],
    inputs: Tuple[float, float, float, float],
    params: QuadcopterModelParams,
) -> Tuple[float, ...]:
    x, y, z, phi, theta, psi, vx, vy, vz, omega_x, omega_y, omega_z = state
    thrust, torque_x, torque_y, torque_z = inputs

    # Extract parameters
    m, g, dt = params.mass, params.gravity, params.time_step
    Ix, Iy, Iz = params.inertia

    # Compute accelerations
    ax = (
        (np.cos(phi) * np.sin(theta) * np.cos(psi) + np.sin(phi) * np.sin(psi))
        * thrust
        / m
    )
    ay = (
        (np.cos(phi) * np.sin(theta) * np.sin(psi) - np.sin(phi) * np.cos(psi))
        * thrust
        / m
    )
    az = np.cos(phi) * np.cos(theta) * thrust / m - g

    # Update state
    x_next = x + vx * dt + 0.5 * ax * dt**2
    y_next = y + vy * dt + 0.5 * ay * dt**2
    z_next = z + vz * dt + 0.5 * az * dt**2

    vx_next = vx + ax * dt
    vy_next = vy + ay * dt
    vz_next = vz + az * dt

    phi_next = phi + omega_x * dt
    theta_next = theta + omega_y * dt
    psi_next = psi + omega_z * dt

    omega_x_next = omega_x + torque_x / Ix * dt
    omega_y_next = omega_y + torque_y / Iy * dt
    omega_z_next = omega_z + torque_z / Iz * dt

    return (
        x_next,
        y_next,
        z_next,
        phi_next,
        theta_next,
        psi_next,
        vx_next,
        vy_next,
        vz_next,
        omega_x_next,
        omega_y_next,
        omega_z_next,
    )


class QuadcopterModel(BaseRobotModel):
    base_robot: BaseRobot = BaseRobot(
        params=QuadcopterModelParams,
        inputs=QuadcopterModelInputs,
        state=QuadcopterModelState,
    )

    def __init__(self, params: QuadcopterModelParams) -> None:
        self.params = params

    def reset(self) -> None:
        pass

    def run(
        self,
        state: BaseRobotState,
        inputs: BaseRobotInputs,
        params: Optional[BaseRobotParams] = None,
    ) -> QuadcopterModelState:
        state_q: QuadcopterModelState = cast(QuadcopterModelState, state)
        inputs_q: QuadcopterModelInputs = cast(QuadcopterModelInputs, inputs)
        params_q: QuadcopterModelParams = cast(
            QuadcopterModelParams, params or self.params
        )

        next_state_tup = quadcopter_model(
            state_q.totuple(), inputs_q.totuple(), params_q
        )

        return QuadcopterModelState.fromtuple(next_state_tup)
