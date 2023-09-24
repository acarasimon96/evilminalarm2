# Copyright 2023 Timothy Bautista (acarasimon96).
# SPDX-License-Identifier: Apache-2.0

from colorama import Fore, Style

from . import settings


def tee(text: str):
    # TODO: strip ANSI escape sequences (https://stackoverflow.com/a/14693789/11524425)
    if settings.data.output_file:
        with open(settings.data.output_file, "a") as outfile:
            outfile.write(f"{text}\n")
    print(text)


def debug_print(text: str, color=Fore.WHITE, lpad: int = 0):
    if settings.data.debug:
        assert lpad >= 0, "lpad (leading space width) must be at least 0"
        tee(f"{' ' * lpad}{color}{Style.DIM}{text}{Style.RESET_ALL}")
