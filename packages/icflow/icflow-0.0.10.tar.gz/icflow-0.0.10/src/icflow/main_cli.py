#!/usr/bin/env python3

import argparse
import logging
from pathlib import Path
from icflow.session.parameter_sweep import ParameterSweep

logger = logging.getLogger(__name__)


def sweep(args):
    session = ParameterSweep(args.config)
    session.run()


def main_cli():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dry_run",
        type=int,
        default=0,
        help="Dry run script - 0 can modify, 1 can read, 2 no modify - no read",
    )
    subparsers = parser.add_subparsers(required=True)

    sweep_parser = subparsers.add_parser("sweep")
    sweep_parser.add_argument(
        "--config",
        type=Path,
        required=True,
        help="Path to the config file to use for sweep",
    )
    sweep_parser.set_defaults(func=sweep)
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main_cli()
