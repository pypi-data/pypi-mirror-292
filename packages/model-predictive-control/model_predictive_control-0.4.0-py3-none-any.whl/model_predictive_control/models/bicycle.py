from typing import List, Literal, Optional, Tuple, cast

import numpy as np
from simple_pid import PID

from .base import (
    BaseRobot,
    BaseRobotInputs,
    BaseRobotModel,
    BaseRobotParams,
    BaseRobotState,
)


class BicycleModelParams(BaseRobotParams):
    time_step: float
    steering_ratio: float
    wheel_base: float
    speed_kp: float
    speed_ki: float
    speed_kd: float
    throttle_min: float
    throttle_max: float
    throttle_gain: float
    origin: Literal["rear_axel_center", "wheel_base_center"] = (
        "rear_axel_center"
    )


class BicycleModelState(BaseRobotState):
    x: float
    y: float
    theta: float
    velocity: float

    def totuple(
        self,
    ) -> Tuple[float, float, float, float]:
        return (
            self.x,
            self.y,
            self.theta,
            self.velocity,
        )

    @staticmethod
    def fromtuple(x: Tuple[float, float, float, float]) -> "BicycleModelState":
        assert len(x) == 4
        return BicycleModelState(
            x=x[0],
            y=x[1],
            theta=x[2],
            velocity=x[3],
        )


class BicycleModelInputs(BaseRobotInputs):
    steering_angle: float
    desired_velocity: float

    def totuple(
        self,
    ) -> Tuple[float, float]:
        return (
            self.steering_angle,
            self.desired_velocity,
        )

    @staticmethod
    def fromtuple(x: Tuple[float, float]) -> "BicycleModelInputs":
        assert len(x) == 2
        return BicycleModelInputs(
            steering_angle=x[0],
            desired_velocity=x[1],
        )


def bicycle_model_rear_axel_center(
    x: Tuple[float, float, float, float],
    u: float,
    velocity: float,
    steering_ratio: float,
    wheel_base: float,
    time_step: float,
) -> Tuple[float, float, float, float]:
    """
    x <- (X, Y, theta, velocity)
    u <- steering angle
    """
    delta = np.radians(u) / steering_ratio
    x_next: List[float] = [
        0.0,
        0.0,
        0.0,
        0.0,
    ]
    x_next[2] = x[2] + (
        velocity / wheel_base * np.tan(delta) * time_step
    )  # theta
    x_next[0] = x[0] + (velocity * np.cos(x_next[2]) * time_step)  # x pos
    x_next[1] = x[1] + (velocity * np.sin(x_next[2]) * time_step)  # y pos
    x_next[3] = velocity
    return (x_next[0], x_next[1], x_next[2], x_next[3])


def bicycle_model_wheel_base_center(
    x: Tuple[float, float, float, float],
    u: float,
    velocity: float,
    steering_ratio: float,
    wheel_base: float,
    time_step: float,
) -> Tuple[float, float, float, float]:
    """
    x <- (X, Y, theta, velocity)
    u <- steering angle
    Origin is at the center of the wheelbase
    """
    delta = np.radians(u) / steering_ratio
    x_next: List[float] = [0.0, 0.0, 0.0, 0.0]

    # Calculate change in theta
    delta_theta = velocity / wheel_base * np.tan(delta) * time_step
    x_next[2] = x[2] + delta_theta  # theta

    # Calculate displacement of the center point
    displacement = velocity * time_step

    # Calculate new position
    x_next[0] = x[0] + displacement * np.cos(x[2] + delta_theta / 2)  # x pos
    x_next[1] = x[1] + displacement * np.sin(x[2] + delta_theta / 2)  # y pos
    x_next[3] = velocity

    return (x_next[0], x_next[1], x_next[2], x_next[3])


class BicycleModel(BaseRobotModel):

    base_robot: BaseRobot = BaseRobot(
        params=BicycleModelParams,
        inputs=BicycleModelInputs,
        state=BicycleModelState,
    )

    def __init__(
        self,
        params: BicycleModelParams,
    ) -> None:
        self.speed_pid = PID()
        self.set_params(params)

    def set_params(self, params: BicycleModelParams):
        self.steering_ratio = params.steering_ratio
        self.wheel_base = params.wheel_base
        self.time_step = params.time_step
        self.throttle_gain = params.throttle_gain

        self.speed_pid.Kp, self.speed_pid.Ki, self.speed_pid.Kd = (
            params.speed_kp,
            params.speed_ki,
            params.speed_kd,
        )
        self.speed_pid.sample_time = self.time_step  # seconds
        self.speed_pid.output_limits = (
            params.throttle_min,
            params.throttle_max,
        )
        self.origin = params.origin

    def reset(self) -> None:
        self.speed_pid.reset()

    def run(
        self,
        state: BaseRobotState,
        inputs: BaseRobotInputs,
        params: Optional[BaseRobotParams] = None,
    ) -> BicycleModelState:

        state_m: BicycleModelState = cast(BicycleModelState, state)
        inputs_m: BicycleModelInputs = cast(BicycleModelInputs, inputs)
        params_m: BicycleModelParams = cast(BicycleModelParams, params)

        if params_m is not None:
            self.set_params(params_m)

        self.speed_pid.setpoint = inputs_m.desired_velocity
        throttle = self.speed_pid(state_m.velocity)
        assert isinstance(throttle, float)
        acceleration = self.throttle_gain * throttle
        new_velocity = acceleration * self.time_step

        state_m.velocity = new_velocity

        if self.origin == "rear_axel_center":
            next_state_tup = bicycle_model_rear_axel_center(
                state_m.totuple(),
                inputs_m.steering_angle,
                inputs_m.desired_velocity,
                self.steering_ratio,
                self.wheel_base,
                self.time_step,
            )
        elif self.origin == "wheel_base_center":
            next_state_tup = bicycle_model_wheel_base_center(
                state_m.totuple(),
                inputs_m.steering_angle,
                inputs_m.desired_velocity,
                self.steering_ratio,
                self.wheel_base,
                self.time_step,
            )
        else:
            raise ValueError(f"Unknown origin: {self.origin}")

        return BicycleModelState.fromtuple(next_state_tup)
