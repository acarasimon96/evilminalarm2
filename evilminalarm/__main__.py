# Copyright 2023 Timothy Bautista (acarasimon96).
# SPDX-License-Identifier: Apache-2.0

from datetime import datetime

from colorama import Fore, Style

from . import __version__
from .core import Core
from .logging import debug_print, tee
from .settings import load_config


def main():
    tee(
        f"{Fore.RED}{Style.BRIGHT}"
        f"Evil Minutes of the Clock Alarms 2 v{__version__}\n"
        f"{Style.NORMAL}A customizable Python alarm\n\n"
        f"{Fore.RESET}{Style.BRIGHT}"
        "Press Ctrl+C or send a SIGINT to this process to exit\n"
        f"{Style.RESET_ALL}"
    )
    load_config()
    Core().run()
    debug_print(f"+++ Exited properly at {datetime.now().strftime('%H:%M:%S')} +++")


if __name__ == "__main__":
    main()
