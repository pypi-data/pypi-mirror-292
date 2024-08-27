import pytest
import numpy as np
from model_predictive_control.mpc import MPC
from model_predictive_control.models.quadcopter import (
    QuadcopterModel,
    QuadcopterModelParams,
)
from model_predictive_control.cost.quadcopter_trajectory_penalty import (
    QuadcopterTrajectoryPenalty,
)

# Fixtures for creating necessary instances


@pytest.fixture
def quadcopter_model():
    params = QuadcopterModelParams(
        time_step=0.1,
        mass=1.0,
        inertia=(0.01, 0.01, 0.02),
        arm_length=0.2,
    )
    return QuadcopterModel(params)


@pytest.fixture
def cost(quadcopter_model):
    return QuadcopterTrajectoryPenalty(model=quadcopter_model)


@pytest.fixture
def mpc(quadcopter_model, cost):
    return MPC(
        model=quadcopter_model,
        cost=cost,
        horizon=20,
        state_dim=12,
        controls_dim=4,
    )


@pytest.fixture
def start_state():
    return [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]


@pytest.fixture
def desired_state_sequence():
    t = np.linspace(0, 2 * np.pi, 20)
    radius = 1.0
    return [
        [
            radius * angle / (2 * np.pi) * np.cos(angle),
            radius * angle / (2 * np.pi) * np.sin(angle),
            0.1 * angle,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
        ]
        for angle in t
    ]


@pytest.fixture
def initial_control_sequence():
    hover_thrust = 1.0 * 9.81
    return [[hover_thrust, 0.0, 0.0, 0.0] for _ in range(20)]


@pytest.fixture
def bounds():
    hover_thrust = 1.0 * 9.81
    max_thrust = 2 * hover_thrust
    max_torque = 1.0
    return [
        [
            (0, max_thrust),
            (-max_torque, max_torque),
            (-max_torque, max_torque),
            (-max_torque, max_torque),
        ]
        for _ in range(20)
    ]


@pytest.fixture
def max_iters():
    return 50


# Test cases


def test_initialization(mpc, quadcopter_model, cost):
    assert mpc.model == quadcopter_model
    assert mpc.cost == cost
    assert mpc.horizon == 20
    assert mpc.state_dim == 12
    assert mpc.controls_dim == 4


def test_step_shape(
    mpc,
    start_state,
    desired_state_sequence,
    initial_control_sequence,
    bounds,
    max_iters,
):
    control_sequence = mpc.step(
        start_state,
        desired_state_sequence,
        initial_control_sequence,
        bounds,
        max_iters,
    )
    assert isinstance(control_sequence, list)
    assert len(control_sequence) == 20
    assert all(len(ctrl) == 4 for ctrl in control_sequence)


def test_invalid_model():
    class InvalidModel:
        pass

    with pytest.raises(AssertionError):
        MPC(
            model=InvalidModel(),
            cost=None,
            horizon=20,
            state_dim=12,
            controls_dim=4,
        )


def test_cost_function_call(
    mocker,
    mpc,
    start_state,
    desired_state_sequence,
    initial_control_sequence,
    bounds,
    max_iters,
):
    mock_cost = mocker.patch.object(mpc.cost, "cost", return_value=1.0)
    mpc.step(
        start_state,
        desired_state_sequence,
        initial_control_sequence,
        bounds,
        max_iters,
    )
    assert mock_cost.call_count > 0


def test_invalid_input_dimensions(mpc, start_state, desired_state_sequence):
    with pytest.raises(AssertionError):
        invalid_control_sequence = [
            [0.0, 0.0, 0.0] for _ in range(20)
        ]  # Incorrect controls_dim
        mpc.step(
            start_state,
            desired_state_sequence,
            invalid_control_sequence,
            bounds=[[(0.0, 1.0)] for _ in range(20)],
            max_iters=50,
        )

    with pytest.raises(AssertionError):
        invalid_start_state = [0.0, 0.0]  # Incorrect state_dim
        mpc.step(
            invalid_start_state,
            desired_state_sequence,
            initial_control_sequence=[
                [9.81, 0.0, 0.0, 0.0] for _ in range(20)
            ],
            bounds=[
                [(0.0, 1.0), (0.0, 1.0), (0.0, 1.0), (0.0, 1.0)]
                for _ in range(20)
            ],
            max_iters=50,
        )

    with pytest.raises(AssertionError):
        invalid_desired_state_sequence = [
            [0.0, 0.0, 0.0] for _ in range(20)
        ]  # Incorrect state_dim
        mpc.step(
            start_state,
            invalid_desired_state_sequence,
            initial_control_sequence=[
                [9.81, 0.0, 0.0, 0.0] for _ in range(20)
            ],
            bounds=[
                [(0.0, 1.0), (0.0, 1.0), (0.0, 1.0), (0.0, 1.0)]
                for _ in range(20)
            ],
            max_iters=50,
        )


def test_control_sequence_bounds(
    mpc,
    start_state,
    desired_state_sequence,
    initial_control_sequence,
    bounds,
    max_iters,
):
    control_sequence = mpc.step(
        start_state,
        desired_state_sequence,
        initial_control_sequence,
        bounds,
        max_iters,
    )
    control_sequence_flat = np.array(control_sequence).reshape(-1)
    bounds_flat = np.array(bounds).reshape(-1, 2)
    assert bounds_flat.shape[0] == control_sequence_flat.shape[0]
    for i in range(bounds_flat.shape[0]):
        assert (
            bounds_flat[i][0] <= control_sequence_flat[i] <= bounds_flat[i][1]
        ), f"Value out of bounds ({bounds_flat[i]}) at index {i}: {control_sequence_flat[i]}"
