from __future__ import annotations

from collections.abc import Collection
from ctypes import *
from datetime import datetime

import numpy as np

from .helpers import prepare_coords, prepare_dt, c_double_p, DATADIR
from .echaimlib import echaimlib


def nmf2(lats: np.ndarray, lons: np.ndarray, dt: datetime | Collection) -> np.ndarray:
    """
    Calculate NmF2 index.

    :param lats: Array of latitudes in [deg].
    :param lons: Array of longitudes in [deg].
    :param dt: A single datetime object or a sequence of datetime objects.
    :return: 1D numpy array with shape len(lats).
    """
    if not lats.size == lons.size:
        raise ValueError("Shapes of lat and lon arrays must be the same.")
    lats = lats.astype(np.float64)
    lons = lons.astype(np.float64)
    lats_p, lons_p, l0 = prepare_coords(lats, lons)
    year_p, month_p, day_p, hour_p, minute_p, second_p = prepare_dt(dt, len(lats))

    output = np.empty(len(lats), dtype=np.float64)
    output_p = output.ctypes.data_as(c_double_p)

    echaimlib.pyNmF2(output_p, DATADIR.encode("utf-8"),
                     lats_p, lons_p, year_p, month_p, day_p,
                     hour_p, minute_p, second_p, l0, c_int(0))
    return output


def nmf2_storm(lats: np.ndarray, lons: np.ndarray, dt: datetime | Collection) -> np.ndarray:
    """
    Calculate NmF2 index using storm perturbation model.

    :param lats: Array of latitudes in [deg].
    :param lons: Array of longitudes in [deg].
    :param dt: A single datetime object or a sequence of datetime objects.
    :return: 1D numpy array with shape len(lats).
    """
    if not lats.size == lons.size:
        raise ValueError("Shapes of lat and lon arrays must be the same.")
    lats = lats.astype(np.float64)
    lons = lons.astype(np.float64)
    lats_p, lons_p, l0 = prepare_coords(lats, lons)
    year_p, month_p, day_p, hour_p, minute_p, second_p = prepare_dt(dt, len(lats))

    output = np.empty(len(lats), dtype=np.float64)
    output_p = output.ctypes.data_as(c_double_p)

    echaimlib.pyNmF2Storm(output_p, DATADIR.encode("utf-8"),
                          lats_p, lons_p, year_p, month_p, day_p,
                          hour_p, minute_p, second_p, l0, c_int(0))
    return output


def hmf2(lats: np.ndarray, lons: np.ndarray, dt: datetime | Collection) -> np.ndarray:
    """
    Calculate HmF2 index.

    :param lats: Array of latitudes in [deg].
    :param lons: Array of longitudes in [deg].
    :param dt: A single datetime object or a sequence of datetime objects.
    :return: 1D numpy array with shape len(lats).
    """
    if not lats.size == lons.size:
        raise ValueError("Shapes of lat and lon arrays must be the same.")
    lats = lats.astype(np.float64)
    lons = lons.astype(np.float64)
    lats_p, lons_p, l0 = prepare_coords(lats, lons)
    year_p, month_p, day_p, hour_p, minute_p, second_p = prepare_dt(dt, len(lats))

    output = np.empty(len(lats), dtype=np.float64)
    output_p = output.ctypes.data_as(c_double_p)

    echaimlib.pyHmF2(output_p, DATADIR.encode("utf-8"),
                     lats_p, lons_p, year_p, month_p, day_p,
                     hour_p, minute_p, second_p, l0, c_int(0))
    return output


def hmf1(lats: np.ndarray, lons: np.ndarray, dt: datetime | Collection) -> np.ndarray:
    """
    Calculate HmF1 index.

    :param lats: Array of latitudes in [deg].
    :param lons: Array of longitudes in [deg].
    :param dt: A single datetime object or a sequence of datetime objects.
    :return: 1D numpy array with shape len(lats).
    """
    if not lats.size == lons.size:
        raise ValueError("Shapes of lat and lon arrays must be the same.")
    lats = lats.astype(np.float64)
    lons = lons.astype(np.float64)
    lats_p, lons_p, l0 = prepare_coords(lats, lons)
    year_p, month_p, day_p, hour_p, minute_p, second_p = prepare_dt(dt, len(lats))

    output = np.empty(len(lats), dtype=np.float64)
    output_p = output.ctypes.data_as(c_double_p)

    echaimlib.pyHmF1(output_p, DATADIR.encode("utf-8"),
                     lats_p, lons_p, year_p, month_p, day_p,
                     hour_p, minute_p, second_p, l0, c_int(0))
    return output
