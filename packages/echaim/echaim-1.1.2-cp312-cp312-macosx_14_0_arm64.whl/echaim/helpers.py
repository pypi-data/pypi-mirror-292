from collections.abc import Collection
from ctypes import *
from datetime import datetime
import numpy as np
import os

c_double_p = POINTER(c_double)
c_int_p = POINTER(c_int)

DATADIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), "model_data/")


def prepare_coords(lats: np.ndarray, lons: np.ndarray):
    l0 = c_int(len(lats))
    lats_p = lats.ctypes.data_as(c_double_p)
    lons_p = lons.ctypes.data_as(c_double_p)
    return lats_p, lons_p, l0


def prepare_dt(dt, ndates):
    if isinstance(dt, datetime):
        dts = [dt] * ndates
    elif isinstance(dt, Collection):
        if len(dt) != ndates:
            raise ValueError("The length of array of datetimes must have the same size as coordinates arrays.")
        else:
            dts = dt
    else:
        raise ValueError("Incorrect type of dt parameter.")
    year_p = np.array([dt.year for dt in dts], dtype=np.int32).ctypes.data_as(c_int_p)
    month_p = np.array([dt.month for dt in dts], dtype=np.int32).ctypes.data_as(c_int_p)
    day_p = np.array([dt.day for dt in dts], dtype=np.int32).ctypes.data_as(c_int_p)
    hour_p = np.array([dt.hour for dt in dts], dtype=np.int32).ctypes.data_as(c_int_p)
    minute_p = np.array([dt.minute for dt in dts], dtype=np.int32).ctypes.data_as(c_int_p)
    second_p = np.array([dt.second for dt in dts], dtype=np.int32).ctypes.data_as(c_int_p)
    return year_p, month_p, day_p, hour_p, minute_p, second_p
