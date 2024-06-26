# Copyright 2023 Timothy Bautista (acarasimon96).
# SPDX-License-Identifier: Apache-2.0

from datetime import datetime, time

import yaml
from attrs import define, field
from cattrs import BaseConverter

from .backends import AVAILABLE_BACKENDS

CONFIG_FILENAME = "config.yaml"


@define
class SoundSpec:
    file: str
    volume: float = field(converter=float)

    @volume.validator  # type: ignore
    def _validate_volume(self, attr, value):
        if value < 0.0:
            raise ValueError("volume must be at least 0")


@define
class Config:
    sounds: dict[str, SoundSpec] = field(default={})

    debug: bool = False
    backend: str = field(default="paplay", converter=lambda s: s.lower())
    start_time: time = time(0, 0)
    end_time: time = time(23, 59)
    sounds_dir: str = "./sounds"
    minutes: dict[int, str] = {}
    times: dict[time, str] = {}
    output_file: str = ""
    lag_threshold_ms: float = field(default=75, converter=float)
    target_ms: float = field(default=0, converter=float)

    @backend.validator  # type: ignore
    def _validate_backend(self, attr, value):
        if value not in AVAILABLE_BACKENDS:
            raise ValueError(
                f'Backend "{value}" not found.'
                f" Available backends: {', '.join(AVAILABLE_BACKENDS.keys())}"
            )

    @sounds.validator  # type: ignore
    def _validate_sounds(self, attr, value):
        if not value:
            raise ValueError("No sounds are defined")


data: Config = None


def load_config(config_path: str = CONFIG_FILENAME):
    global data

    def time_structure_hook(time_str, _) -> time:
        if len(time_str.split(":")) != 3:
            time_str = f"{time_str}:00"
        return datetime.strptime(time_str, "%H:%M:%S").time()

    loaded_config: dict
    with open(config_path) as f:
        loaded_config = yaml.safe_load(f)

    converter = BaseConverter()
    converter.register_structure_hook(time, time_structure_hook)
    data = converter.structure(loaded_config, Config)

    # Prepend sounds directory path to all filenames
    for soundspec in data.sounds.values():
        soundspec.file = f"{data.sounds_dir}/{soundspec.file}"
