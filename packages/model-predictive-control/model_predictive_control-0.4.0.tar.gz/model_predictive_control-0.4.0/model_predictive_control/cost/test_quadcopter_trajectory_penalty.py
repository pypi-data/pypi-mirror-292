import pytest

from model_predictive_control.cost.quadcopter_trajectory_penalty import (
    QuadcopterTrajectoryPenalty,
)
from model_predictive_control.models.quadcopter import (
    QuadcopterModel,
    QuadcopterModelParams,
)

# Fixtures for creating necessary instances and states


@pytest.fixture
def quadcopter_model():
    params = QuadcopterModelParams(
        time_step=0.1,
        mass=1.0,
        inertia_xx=0.01,
        inertia_yy=0.01,
        inertia_zz=0.01,
        arm_length=0.2,
        thrust_coefficient=1e-6,
        drag_coefficient=1e-6,
    )
    return QuadcopterModel(params)


@pytest.fixture
def traj_cost(quadcopter_model):
    return QuadcopterTrajectoryPenalty(model=quadcopter_model)


@pytest.fixture
def input_sequence():
    return [
        (0.0, 0.0, 0.0, 1.0),  # (torque_x, torque_y, torque_z, thrust)
        (0.0, 0.0, 0.0, 1.0),
        (0.0, 0.0, 0.0, 1.0),
    ]


@pytest.fixture
def current_state():
    return (
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
    )  # (x, y, z, phi, theta, psi, vx, vy, vz, omega_x, omega_y, omega_z)


@pytest.fixture
def desired_state_sequence():
    return [
        (1.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0),
        (2.0, 2.0, 2.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0),
        (3.0, 3.0, 3.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0),
    ]


# Test cases


def test_initialization(traj_cost):
    assert traj_cost.position_penalty == 1.0
    assert traj_cost.orientation_penalty == 0.1
    assert traj_cost.velocity_penalty == 0.01
    assert traj_cost.angular_velocity_penalty == 0.01
    assert traj_cost.input_penalty == 0.001


def test_unsupported_model_error():
    class UnsupportedModel:
        pass

    with pytest.raises(AssertionError):
        model = QuadcopterTrajectoryPenalty(model=UnsupportedModel())
        cost = model.cost(
            [(0, 0, 0, 0)],
            (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
            [(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)],
        )
        print(cost)


def test_cost_calculation(
    traj_cost, input_sequence, current_state, desired_state_sequence
):
    cost_val = traj_cost.cost(
        input_sequence, current_state, desired_state_sequence
    )
    assert cost_val > 0  # Basic check that cost is calculated


def test_missing_x_attribute(
    traj_cost, input_sequence, desired_state_sequence
):
    current_state_invalid = (
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
    )  # Missing one of the attributes
    with pytest.raises(AssertionError):
        traj_cost.cost(
            input_sequence, current_state_invalid, desired_state_sequence
        )


def test_missing_torque_attribute(
    traj_cost, current_state, desired_state_sequence
):
    input_sequence_invalid = [
        (0.0, 0.0, 0.0, 1.0),  # Correct
        (0.0, 1.0),  # Missing some torque components
        (0.0, 0.0, 0.0, 1.0),
    ]
    with pytest.raises(AssertionError):
        traj_cost.cost(
            input_sequence_invalid, current_state, desired_state_sequence
        )


def test_cost_calculation_zero_penalty(
    traj_cost, input_sequence, current_state, desired_state_sequence
):
    # Override penalties to be zero to test if cost also results in zero
    traj_cost.position_penalty = 0.0
    traj_cost.orientation_penalty = 0.0
    traj_cost.velocity_penalty = 0.0
    traj_cost.angular_velocity_penalty = 0.0
    traj_cost.input_penalty = 0.0

    cost_val = traj_cost.cost(
        input_sequence, current_state, desired_state_sequence
    )
    assert cost_val == 0.0  # If penalties are zero, cost should also be zero


def test_input_penalty_only(
    traj_cost, input_sequence, current_state, desired_state_sequence
):
    # Override penalties to test input penalty independently
    traj_cost.position_penalty = 0.0
    traj_cost.orientation_penalty = 0.0
    traj_cost.velocity_penalty = 0.0
    traj_cost.angular_velocity_penalty = 0.0
    traj_cost.input_penalty = 0.001

    cost_val = traj_cost.cost(
        input_sequence, current_state, desired_state_sequence
    )
    expected_cost = (
        sum((0.0**2 + 0.0**2 + 0.0**2 + 1.0**2) for _ in input_sequence)
        * 0.001
    )
    assert cost_val == pytest.approx(
        expected_cost
    )  # Check if input penalty is computed correctly


def test_position_penalty_only(
    traj_cost, input_sequence, current_state, desired_state_sequence
):
    # Override penalties to test position penalty independently
    traj_cost.position_penalty = 1.0
    traj_cost.orientation_penalty = 0.0
    traj_cost.velocity_penalty = 0.0
    traj_cost.angular_velocity_penalty = 0.0
    traj_cost.input_penalty = 0.0

    # Mock the run method to avoid dynamic state changes for simplicity
    original_run_method = traj_cost.model.run

    def mock_run(state, inputs):
        return state

    traj_cost.model.run = mock_run

    cost_val = traj_cost.cost(
        input_sequence, current_state, desired_state_sequence
    )
    expected_cost = (
        sum(
            ((0.0 - 1.0) ** 2 + (0.0 - 1.0) ** 2 + (0.0 - 1.0) ** 2),
            ((0.0 - 2.0) ** 2 + (0.0 - 2.0) ** 2 + (0.0 - 2.0) ** 2),
            ((0.0 - 3.0) ** 2 + (0.0 - 3.0) ** 2 + (0.0 - 3.0) ** 2),
        )
        * 1.0
    )
    assert cost_val == pytest.approx(
        expected_cost
    )  # Check if position penalty is computed correctly

    # Restore the original method
    traj_cost.model.run = original_run_method
