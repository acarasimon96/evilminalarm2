# Copyright 2023 Timothy Bautista (acarasimon96).
# SPDX-License-Identifier: Apache-2.0

import subprocess

from ..logging import debug_print
from ._base import PlayerBackend


class PaplayBackend(PlayerBackend):
    def play(self, path: str, volume: float | int = 100):
        args = [
            "paplay",
            '--client-name="paplay - evilminalarm"',
            "--latency-msec=100",
            f'"{path}"',
        ]

        # Process volume
        assert volume >= 0, "volume must be at least zero"
        args.insert(2, f"--volume={round(volume / 100 * 65535)}")

        debug_print(str(args), lpad=8)
        # Using this instead of os.shell for core to be able to catch KeyboardInterrupt
        subprocess.call(" ".join(args), shell=True)

    def stop(self):
        # Propagate KeyboardInterrupt to child process to stop playing sound
        # (see https://stackoverflow.com/a/18740180/11524425)
        pass
