# Copyright 2023 Timothy Bautista (acarasimon96).
# SPDX-License-Identifier: Apache-2.0


class PlayerBackend:
    def play(self, path: str, volume: float | int = 100):
        raise NotImplementedError

    def stop(self):
        raise NotImplementedError

    def clean_up(self):
        pass
