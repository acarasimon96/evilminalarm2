# Copyright 2023 Timothy Bautista (acarasimon96).
# SPDX-License-Identifier: Apache-2.0

from datetime import datetime

from colorama import Fore, Style

from . import __version__, settings
from .core import Core
from .logging import debug_print, tee


def main():
    settings.load_config()

    tee(
        f"{Fore.RED}{Style.BRIGHT}"
        f"Evil Minutes of the Clock Alarms 2 v{__version__}\n"
        f"{Style.NORMAL}A customizable Python alarm\n\n"
        f"{Fore.RESET}{Style.BRIGHT}"
        "Press Ctrl+C or send a SIGINT to this process to exit\n"
        f"{Style.RESET_ALL}"
    )
    debug_print(f"Using sounds directory: {settings.data.sounds_dir}")

    Core().run()

    debug_print(f"+++ Exited properly at {datetime.now().strftime('%H:%M:%S')} +++\n")


if __name__ == "__main__":
    main()
