# Copyright 2023 Timothy Bautista (acarasimon96).
# SPDX-License-Identifier: Apache-2.0

from datetime import datetime, timedelta
from time import sleep, time_ns
from typing import TYPE_CHECKING, Any, Optional

from colorama import Fore, Style

from .backends import AVAILABLE_BACKENDS
from .logging import debug_print, tee
from .settings import config

if TYPE_CHECKING:
    from .backends._base import PlayerBackend


def alarm_msg_print(msg: str):
    lpad = 8 if config["debug"] else 0
    tee(f"{' ' * lpad}{Style.BRIGHT}{msg} - press Ctrl+C to stop{Style.RESET_ALL}")


# TODO: move to separate module for use in other modules
def get_ms() -> float:
    return time_ns() % 60_000_000_000 / 1_000_000


class Core:
    def __init__(self):
        backend_name: str = config["backend"]
        player_class = AVAILABLE_BACKENDS.get(backend_name)
        assert player_class, (
            f'Backend "{backend_name}" not found.'
            f" Available backends: {', '.join(AVAILABLE_BACKENDS.keys())}"
        )
        self.player: PlayerBackend = player_class()
        debug_print(f"Using backend: {backend_name} ({player_class})")

    def trigger_alarm(self, minute: datetime):
        # Don't do anything if outside alarm period
        minute_time = minute.time()
        if not config["start_time"] <= minute_time <= config["end_time"]:
            return

        spec_name = ""
        # Specific times (takes precedence over hourly alarms)
        if (hour_min_pair := minute_time.replace(second=0, microsecond=0)) in config[
            "times"
        ]:
            alarm_msg_print(
                f"Playing alarm for specific time: {minute.strftime('%H:%M')}"
            )
            spec_name = config["times"][hour_min_pair]
        # Hourly alarms
        elif (current_min := minute.minute) in config["minutes"]:
            alarm_msg_print(f"Playing alarm for :{current_min:02d}")
            spec_name = config["minutes"][current_min]

        spec: Optional[dict[str, Any]] = config["sounds"].get(spec_name)
        if spec:
            debug_print(f"play_sound lag: {get_ms():.2f} ms", lpad=8)
            try:
                # This function must *always* block for this to work properly
                self.player.play(spec["file"], spec["volume"])
            except KeyboardInterrupt:
                self.player.stop()
                debug_print("play_sound interrupted", lpad=8)
            else:
                debug_print("play_sound finished", lpad=8)

    def run(self):
        while True:
            try:
                next_min = (datetime.now() + timedelta(seconds=60)).replace(
                    second=0, microsecond=0
                )
                sleep((next_min - datetime.now()).total_seconds())

                # Measure wake lag
                ms = get_ms()
                msg = f"[{next_min.strftime('%H:%M')}] Wake lag: {ms:.2f} ms"
                if ms >= config["lag_threshold_ms"]:
                    debug_print(msg, Fore.RED)
                elif ms >= config["target_ms"] + 1.0:
                    debug_print(msg, Fore.YELLOW)
                else:
                    debug_print(msg)

                # Keep sleeping until target lag ms reached
                if ms < config["target_ms"]:
                    sleep((config["target_ms"] - ms) / 1000)
                    debug_print(f"Compensated wake lag: {get_ms():.2f} ms", lpad=8)

                self.trigger_alarm(next_min)
            except KeyboardInterrupt:
                debug_print("\nReceived KeyboardInterrupt. Shutting down...")
                break

        self.player.clean_up()
