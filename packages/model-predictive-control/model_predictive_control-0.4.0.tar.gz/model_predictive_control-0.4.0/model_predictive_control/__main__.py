"""Entry point for model_predictive_control."""

import argparse

from model_predictive_control.cli_bicycle import (
    main as main_bicycle,
)  # pragma: no cover
from model_predictive_control.cli_drone import (
    main as main_drone,
)  # pragma: no cover


def main():
    parser = argparse.ArgumentParser(
        description="Model Predictive Control Demos"
    )
    parser.add_argument(
        "demo",
        choices=[
            "bicycle_rear_axel_center",
            "bicycle_wheel_base_center",
            "drone",
        ],
        help="Which demo to run: 'bicycle' or 'drone'",
        nargs="?",
        default="bicycle",
    )

    args = parser.parse_args()
    demo = args.demo

    if demo == "bicycle_rear_axel_center":
        main_bicycle(origin="rear_axel_center")
    elif demo == "drone":
        main_drone()
    elif demo == "bicycle_wheel_base_center":
        main_bicycle(origin="wheel_base_center")
    else:
        parser.print_help()
        print("Unknown demo")


if __name__ == "__main__":  # pragma: no cover
    main()
