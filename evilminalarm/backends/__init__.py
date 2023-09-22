# Copyright 2023 Timothy Bautista (acarasimon96).
# SPDX-License-Identifier: Apache-2.0

from .paplay import PaplayBackend

AVAILABLE_BACKENDS = {
    "paplay": PaplayBackend,
}
