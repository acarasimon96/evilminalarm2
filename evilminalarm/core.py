# Copyright 2023 Timothy Bautista (acarasimon96).
# SPDX-License-Identifier: Apache-2.0

from datetime import datetime, timedelta
from time import sleep, time_ns
from typing import TYPE_CHECKING, Optional

from colorama import Fore, Style

from . import settings
from .backends import AVAILABLE_BACKENDS
from .logging import debug_print, tee

if TYPE_CHECKING:
    from .backends._base import PlayerBackend
    from .settings import SoundSpec


def alarm_msg_print(msg: str):
    lpad = 11 if settings.data.debug else 0
    tee(f"{' ' * lpad}{Style.BRIGHT}{msg} - press Ctrl+C to stop{Style.RESET_ALL}")


# TODO: move to separate module for use in other modules
def get_ms() -> float:
    return time_ns() % 1_000_000_000 / 1_000_000


class Core:
    def __init__(self):
        backend_name: str = settings.data.backend
        player_class = AVAILABLE_BACKENDS[backend_name]
        self.player: PlayerBackend = player_class()
        debug_print(f"Using backend: {backend_name} ({player_class})")

    def trigger_alarm(self, trigger_dt: datetime):
        # Don't do anything if outside alarm period
        trigger_time = trigger_dt.time().replace(microsecond=0)
        if not settings.data.start_time <= trigger_time <= settings.data.end_time:
            return

        spec_name = ""
        # Specific times (takes precedence over hourly alarms)
        if trigger_time in settings.data.times:
            alarm_msg_print(
                f"Playing alarm for specific time: {trigger_dt.strftime('%H:%M:%S')}"
            )
            spec_name = settings.data.times[trigger_time]
        # Hourly alarms
        elif (current_min := trigger_dt.minute) in settings.data.minutes:
            alarm_msg_print(f"Playing alarm for :{current_min:02d}")
            spec_name = settings.data.minutes[current_min]

        spec: Optional[SoundSpec] = settings.data.sounds.get(spec_name)
        if spec:
            debug_print(f"play_sound lag: {get_ms():.2f} ms", lpad=11)
            try:
                # This function must *always* block for this to work properly
                self.player.play(spec.file, spec.volume)
            except KeyboardInterrupt:
                self.player.stop()
                debug_print("play_sound interrupted", lpad=11)
            else:
                debug_print("play_sound finished", lpad=11)

    def run(self):
        sorted_times: list[timedelta] = sorted(
            timedelta(seconds=t.hour * 3600 + t.minute * 60 + t.second)
            for t in settings.data.times.keys()
        )
        _td_60 = timedelta(seconds=60)
        _td_0 = timedelta()

        while True:
            try:
                now = datetime.now()
                next_trigger = (now + _td_60).replace(second=0, microsecond=0)

                # Get next trigger time according to `config.times` dict
                now_as_td = timedelta(
                    seconds=now.hour * 3600 + now.minute * 60 + now.second
                )
                next_time = next(
                    filter(lambda t: _td_0 < t - now_as_td <= _td_60, sorted_times),
                    None,
                )
                if next_time and next_time < timedelta(
                    seconds=next_trigger.hour * 3600
                    + next_trigger.minute * 60
                    + next_trigger.second
                ):
                    next_trigger = next_trigger.replace(
                        hour=next_time.seconds // 3600 % 24,
                        minute=next_time.seconds // 60 % 60,
                        second=next_time.seconds % 60,
                    )

                # Try to minimize sleep lag by refreshing `now`
                sleep((next_trigger - datetime.now()).total_seconds())

                # Measure wake lag
                ms = get_ms()
                msg = f"[{next_trigger.strftime('%H:%M:%S')}] Wake lag: {ms:.2f} ms"
                if ms >= settings.data.lag_threshold_ms:
                    debug_print(msg, Fore.RED)
                elif ms >= settings.data.target_ms + 1.0:
                    debug_print(msg, Fore.YELLOW)
                else:
                    debug_print(msg)

                # Keep sleeping until target lag ms reached
                if ms < settings.data.target_ms:
                    sleep((settings.data.target_ms - ms) / 1000)
                    debug_print(f"Compensated wake lag: {get_ms():.2f} ms", lpad=11)

                self.trigger_alarm(next_trigger)

            except KeyboardInterrupt:
                debug_print("\nReceived KeyboardInterrupt. Shutting down...")
                break

        self.player.clean_up()
