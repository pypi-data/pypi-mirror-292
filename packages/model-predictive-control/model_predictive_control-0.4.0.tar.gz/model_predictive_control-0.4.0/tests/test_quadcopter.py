import pytest
import numpy as np
from model_predictive_control.models.quadcopter import (
    QuadcopterModel,
    QuadcopterModelParams,
    QuadcopterModelState,
    QuadcopterModelInputs,
    quadcopter_model,
)


@pytest.fixture
def default_params():
    return QuadcopterModelParams(
        time_step=0.1,
        mass=1.0,
        inertia=(0.01, 0.01, 0.02),
        arm_length=0.5,
        gravity=9.81,
    )


@pytest.fixture
def initial_state():
    return QuadcopterModelState(
        x=0.0,
        y=0.0,
        z=0.0,
        phi=0.0,
        theta=0.0,
        psi=0.0,
        vx=0.0,
        vy=0.0,
        vz=0.0,
        omega_x=0.0,
        omega_y=0.0,
        omega_z=0.0,
    )


@pytest.fixture
def default_inputs():
    return QuadcopterModelInputs(
        thrust=9.81, torque_x=0.0, torque_y=0.0, torque_z=0.0
    )


@pytest.fixture
def quadcopter_model_instance(default_params):
    return QuadcopterModel(default_params)


def test_params_initialization(quadcopter_model_instance, default_params):
    assert (
        quadcopter_model_instance.params.time_step == default_params.time_step
    )
    assert quadcopter_model_instance.params.mass == default_params.mass
    assert quadcopter_model_instance.params.inertia == default_params.inertia
    assert (
        quadcopter_model_instance.params.arm_length
        == default_params.arm_length
    )
    assert quadcopter_model_instance.params.gravity == default_params.gravity


def test_state_initialization_and_conversion():
    state = QuadcopterModelState(
        x=1.0,
        y=2.0,
        z=3.0,
        phi=np.pi / 6,
        theta=np.pi / 4,
        psi=np.pi / 3,
        vx=1.0,
        vy=1.0,
        vz=1.0,
        omega_x=0.1,
        omega_y=0.1,
        omega_z=0.1,
    )
    state_tuple = state.totuple()
    assert state_tuple == (
        1.0,
        2.0,
        3.0,
        np.pi / 6,
        np.pi / 4,
        np.pi / 3,
        1.0,
        1.0,
        1.0,
        0.1,
        0.1,
        0.1,
    )

    new_state = QuadcopterModelState.fromtuple(state_tuple)
    assert new_state.x == 1.0
    assert new_state.y == 2.0
    assert new_state.z == 3.0
    assert new_state.phi == np.pi / 6
    assert new_state.theta == np.pi / 4
    assert new_state.psi == np.pi / 3
    assert new_state.vx == 1.0
    assert new_state.vy == 1.0
    assert new_state.vz == 1.0
    assert new_state.omega_x == 0.1
    assert new_state.omega_y == 0.1
    assert new_state.omega_z == 0.1


def test_quadcopter_model_dynamics(default_params):
    x = (
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
    )  # Initial state tuple
    u = (9.81, 0.0, 0.0, 0.0)  # Inputs tuple: thrust equal to gravity to hover
    new_state = quadcopter_model(x, u, default_params)

    assert new_state[0] == x[0]  # X should not have changed
    assert new_state[1] == x[1]  # Y should not have changed
    assert new_state[2] == x[2]  # Z should not have changed (due to thrust)
    assert new_state[3] == x[3]  # Phi should not change due to zero torque
    assert new_state[4] == x[4]  # Theta should not change due to zero torque
    assert new_state[5] == x[5]  # Psi should not change due to zero torque
    assert new_state[6] == x[6]  # vx should not change under hover conditions
    assert new_state[7] == x[7]  # vy should not change under hover conditions
    assert new_state[8] == x[8]  # vz should be zero
    assert new_state[9] == x[9]  # omega_x should not change due to zero torque
    assert (
        new_state[10] == x[10]
    )  # omega_y should not change due to zero torque
    assert (
        new_state[11] == x[11]
    )  # omega_z should not change due to zero torque


def test_full_quadcopter_model_run(
    quadcopter_model_instance, initial_state, default_inputs
):
    new_state = quadcopter_model_instance.run(initial_state, default_inputs)
    assert isinstance(new_state, QuadcopterModelState)
    assert (
        new_state.z == initial_state.z
    )  # Asserting that it maintain altitude
    assert new_state.vz >= initial_state.vz  # Should be accelerating upwards
    assert (
        new_state.phi == initial_state.phi
    )  # No roll change due to zero torque
    assert (
        new_state.theta == initial_state.theta
    )  # No pitch change due to zero torque
    assert (
        new_state.psi == initial_state.psi
    )  # No yaw change due to zero torque
