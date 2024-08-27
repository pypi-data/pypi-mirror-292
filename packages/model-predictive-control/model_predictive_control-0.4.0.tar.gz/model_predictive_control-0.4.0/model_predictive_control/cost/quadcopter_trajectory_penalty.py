from typing import List, Tuple

from ..models.quadcopter import QuadcopterModel
from .base import BaseCost


class QuadcopterTrajectoryPenalty(BaseCost):
    position_penalty: float = 1.0
    orientation_penalty: float = 0.1
    velocity_penalty: float = 0.01
    angular_velocity_penalty: float = 0.01
    input_penalty: float = 0.001

    def __init__(self, model: QuadcopterModel) -> None:
        assert isinstance(model, QuadcopterModel)
        self.model = model

    def cost(
        self,
        input_sequence: List[Tuple],
        current_state_tuple: Tuple,
        desired_state_sequence: List[Tuple],
    ) -> float:
        cost_val = 0.0
        horizon = len(desired_state_sequence)
        self.model.reset()
        current_state = self.model.base_robot.state.fromtuple(
            current_state_tuple
        )

        for i in range(horizon):
            current_input = self.model.base_robot.inputs.fromtuple(
                input_sequence[i]
            )
            current_state = self.model.run(
                state=current_state, inputs=current_input
            )
            desired_state = self.model.base_robot.state.fromtuple(
                desired_state_sequence[i]
            )

            # Position error
            cost_val += self.position_penalty * (
                (current_state.x - desired_state.x) ** 2
                + (current_state.y - desired_state.y) ** 2
                + (current_state.z - desired_state.z) ** 2
            )

            # Orientation error
            cost_val += self.orientation_penalty * (
                (current_state.phi - desired_state.phi) ** 2
                + (current_state.theta - desired_state.theta) ** 2
                + (current_state.psi - desired_state.psi) ** 2
            )

            # Velocity error
            cost_val += self.velocity_penalty * (
                (current_state.vx - desired_state.vx) ** 2
                + (current_state.vy - desired_state.vy) ** 2
                + (current_state.vz - desired_state.vz) ** 2
            )

            # Angular velocity error
            cost_val += self.angular_velocity_penalty * (
                (current_state.omega_x - desired_state.omega_x) ** 2
                + (current_state.omega_y - desired_state.omega_y) ** 2
                + (current_state.omega_z - desired_state.omega_z) ** 2
            )

            # Input penalty
            cost_val += self.input_penalty * (
                current_input.thrust**2
                + current_input.torque_x**2
                + current_input.torque_y**2
                + current_input.torque_z**2
            )

        return cost_val
