import matplotlib.pyplot as plt
import numpy as np

from model_predictive_control.cost.quadcopter_trajectory_penalty import (
    QuadcopterTrajectoryPenalty,
)
from model_predictive_control.models.quadcopter import (
    QuadcopterModel,
    QuadcopterModelInputs,
    QuadcopterModelParams,
    QuadcopterModelState,
)
from model_predictive_control.mpc import MPC


def main():
    # Initialize parameters
    time_step = 0.1
    mass = 1.0  # kg
    arm_length = 0.2  # m
    inertia = (0.01, 0.01, 0.02)  # kg*m^2

    # Initialize the Quadcopter Model
    params = QuadcopterModelParams(
        time_step=time_step,
        mass=mass,
        inertia=inertia,
        arm_length=arm_length,
    )
    quadcopter_model = QuadcopterModel(params)

    # Define the cost function
    cost = QuadcopterTrajectoryPenalty(model=quadcopter_model)

    # Initialize MPC Controller
    horizon = 20
    state_dim = (
        12  # (x, y, z, phi, theta, psi, vx, vy, vz, omega_x, omega_y, omega_z)
    )
    controls_dim = 4  # (thrust, torque_x, torque_y, torque_z)

    mpc = MPC(
        model=quadcopter_model,
        cost=cost,
        horizon=horizon,
        state_dim=state_dim,
        controls_dim=controls_dim,
    )

    # Set up the plot
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection="3d")

    while True:
        for radius in np.arange(0.5, 5, 0.5):
            # Define initial state
            # (x, y, z, phi, theta, psi, vx, vy, vz,
            # omega_x, omega_y, omega_z)
            start_state = [
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
            ]

            # Define desired trajectory: a helical path
            t = np.linspace(0, 2 * np.pi, horizon)
            desired_state_sequence = [
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

            # Initial control sequence: hover thrust and no torques
            hover_thrust = mass * 9.81
            initial_control_sequence = [
                [hover_thrust, 0.0, 0.0, 0.0] for _ in range(horizon)
            ]

            # Define control bounds
            max_thrust = 2 * hover_thrust
            max_torque = 1.0
            bounds = [
                [
                    (0, max_thrust),
                    (-max_torque, max_torque),
                    (-max_torque, max_torque),
                    (-max_torque, max_torque),
                ]
                for _ in range(horizon)
            ]

            # Optimize control inputs using MPC
            optimized_control_sequence = mpc.step(
                start_state_tuple=start_state,
                desired_state_sequence=desired_state_sequence,
                initial_control_sequence=initial_control_sequence,
                bounds=bounds,
                max_iters=50,
            )

            # Simulate the quadcopter using the optimized control inputs
            current_state = start_state
            trajectory = [current_state]

            for controls in optimized_control_sequence:
                state_tuple = tuple(current_state)
                inputs_tuple = tuple(controls)
                inputs_obj = QuadcopterModelInputs.fromtuple(inputs_tuple)
                state_obj = QuadcopterModelState.fromtuple(state_tuple)
                next_state = quadcopter_model.run(state_obj, inputs_obj)
                trajectory.append(list(next_state.totuple()))
                current_state = next_state.totuple()

            # Convert trajectory to numpy array for easier plotting
            trajectory = np.array(trajectory)

            # Clear the previous plot
            ax.clear()

            # Plot the results
            ax.plot(
                [state[0] for state in desired_state_sequence],
                [state[1] for state in desired_state_sequence],
                [state[2] for state in desired_state_sequence],
                label="Desired Trajectory",
                linestyle="--",
                color="g",
            )
            ax.plot(
                trajectory[:, 0],
                trajectory[:, 1],
                trajectory[:, 2],
                label="MPC Trajectory",
                linestyle="-",
                color="b",
            )

            # Set labels and title
            ax.set_xlabel("X position (m)")
            ax.set_ylabel("Y position (m)")
            ax.set_zlabel("Z position (m)")
            ax.set_title("Quadcopter MPC Trajectory vs Desired Trajectory")

            # Set consistent axis limits
            ax.set_xlim(-6, 6)
            ax.set_ylim(-6, 6)
            ax.set_zlim(0, 6)

            ax.legend()
            plt.draw()
            plt.pause(0.001)
            plt.cla()

            # Check for key press to exit
            if plt.waitforbuttonpress(0.001):
                break

    plt.close()


if __name__ == "__main__":
    main()
