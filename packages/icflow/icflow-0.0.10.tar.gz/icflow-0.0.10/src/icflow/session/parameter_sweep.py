"""
This module allows a parameter sweep to be performed.
"""

import logging
import subprocess
import os
import datetime
from pathlib import Path
import itertools
import uuid

import yaml

from icflow.utils.dict_utils import merge_dicts, split_dict_on_type

logger = logging.getLogger()


class ParameterSweep:
    """
    This class is used to implement parameter sweeps driven by an input
    config file.
    """

    def __init__(
        self, config_path: Path, work_dir: Path = Path(), source_dir: Path = Path()
    ) -> None:
        self.config_path = config_path.resolve()
        self.source_dir = source_dir.resolve()
        self.work_dir = work_dir.resolve()
        self.config: dict = {}
        self.title: str = ""
        self.command_line_prefix: str = ""
        self.tasks: list = []

    def read_config(self):
        """
        Read a yaml file at the given path
        """

        logger.info("Reading config from: %s", self.config_path)
        with open(self.config_path, "r", encoding="utf-8") as f:
            self.config = yaml.safe_load(f)

        self.title = self.config["core"]["title"]
        self.command_line_prefix = self.config["core"]["program_call"]

    def _serialize_args(self, cli_args: dict[str, str | None], delimiter="--") -> str:
        """
        Convert command line args given as dict key, value pairs
        to a string format.
        """
        ret = ""
        for key, value in cli_args.items():
            if value is None:
                value = ""
            ret += f" {delimiter}{key} {value}"
        return ret

    def _expand_permutation_dict(self, source: dict) -> list:
        """
        Produce a list of dictionaries from a single dictionary containing list values.
        Each dictionary in this list is a unique permutation from the list entries of
        the original dictionary.
        """
        no_lists, with_lists = split_dict_on_type(source, list)
        items = []
        list_keys, values = zip(*with_lists.items())
        # itertools.product creates all unique permutations of a given iterator
        permutations = itertools.product(*values)
        for perm in permutations:
            # Create a dictionary from the current permutation
            perm_dict = dict(zip(list_keys, perm))
            item = merge_dicts(perm_dict, no_lists)
            items.append(item)
        return items

    def run_tasks(self):
        """
        Run the collected tasks as subprocesses
        """

        current_env = os.environ.copy()
        time = datetime.datetime.now().strftime("%Y-%m-%d_%T")

        logger.info("Setting up work directory at: %s", self.work_dir)
        os.makedirs(self.work_dir, exist_ok=True)

        work_dir = self.work_dir / f"{self.title}_{time}"
        logger.info("Setting up tasks directory at %s", work_dir)
        os.mkdir(work_dir)

        for task in self.tasks:
            output_file = uuid.uuid1()

            task_args = self._serialize_args(task)
            cmd = f"{self.command_line_prefix} {task_args}"

            with open(f"{work_dir}/{output_file}.inp", "w", encoding="utf-8") as f:
                f.write(cmd)
                for key, value in task.items():
                    f.write(f"\n{key}: {value}")

            logger.debug("Launching command: %s", cmd)
            subprocess.run(
                f"{cmd} > {work_dir}/{output_file}.result",
                shell=True,
                check=True,
                env=current_env,
                cwd=self.source_dir,
            )

    def run(self):
        """
        Run a parameter sweep defined by the config at the given path.
        """

        if not self.config:
            self.read_config()

        self.tasks = self._expand_permutation_dict(self.config["parameters"])

        self.run_tasks()
