"""Compatibility import path for ``argos.backend.intel.osint``."""

import sys

from argos.backend.intel.osint import models

sys.modules[f"{__name__}.models"] = models
