# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2024 Scipp contributors (https://github.com/scipp)

import importlib.metadata

from . import components, general, io, sans2d, zoom
from .components import DetectorBankOffset, MonitorOffset, SampleOffset
from .general import default_parameters
from .io import CalibrationFilename
from .visualization import plot_flat_detector_xy

try:
    __version__ = importlib.metadata.version(__package__ or __name__)
except importlib.metadata.PackageNotFoundError:
    __version__ = "0.0.0"

providers = components.providers + general.providers + io.providers

del importlib

__all__ = [
    'CalibrationFilename',
    'DetectorBankOffset',
    'io',
    'MonitorOffset',
    'providers',
    'SampleOffset',
    'plot_flat_detector_xy',
    'sans2d',
    'default_parameters',
    'zoom',
]
