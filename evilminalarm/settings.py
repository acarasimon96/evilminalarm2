# Copyright 2023 Timothy Bautista (acarasimon96).
# SPDX-License-Identifier: Apache-2.0

from datetime import datetime, time

import yaml

CONFIG_FILENAME = "config.yaml"

# Default config
config = {
    "debug": False,
    "backend": "paplay",
    "output_file": "",
    "start_time": time(0, 0),
    "end_time": time(23, 59),
    "sounds_dir": "./sounds",
    "sounds": {
        # "default": {  # noqa
        #     "file": "default.ogg",  # noqa
        #     "volume": 100,  # noqa
        # },
    },
    "minutes": {
        # 29: "default",  # noqa
        # 59: "default",  # noqa
    },
    "times": {
        # time(12, 0): "default",  # noqa
    },
    "lag_threshold_ms": 75.0,
    "target_ms": 0.0,
}


# Based on https://codereview.stackexchange.com/q/269550
def load_config(file_str: str = CONFIG_FILENAME) -> None:
    global config
    with open(file_str) as f:
        loaded_config: dict = yaml.safe_load(f)

        # Process some values
        for k in loaded_config:
            if k in ("start_time", "end_time"):
                loaded_config[k] = datetime.strptime(loaded_config[k], "%H:%M").time()
            if k == "times":
                times_dict_new = {
                    datetime.strptime(k, "%H:%M").time(): v
                    for k, v in loaded_config[k].items()
                }
                loaded_config[k] = times_dict_new
            if k == "sounds":
                for spec_name in loaded_config[k]:
                    loaded_config[k][spec_name][
                        "file"
                    ] = f"{loaded_config['sounds_dir']}/{loaded_config[k][spec_name]['file']}"

        # Can't reassign `config` here as it will unbind it from global var
        config.update(loaded_config)
