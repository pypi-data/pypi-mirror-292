from ctypes import *
from datetime import datetime
from .helpers import prepare_coords, prepare_dt, c_double_p, DATADIR
import numpy as np
from .echaimlib import echaimlib


def update():
    from urllib import request, error
    import os
    location = os.path.dirname(os.path.abspath(__file__))
    try:
        request.urlretrieve(
            'https://chain-new.chain-project.net/echaim_downloads/DBFiles/CHAIM_DB.db',
            os.path.join(location, f'model_data/CHAIM_DB.db')
        )
        print('The index data was successfully updated!')
    except error.URLError:
        print('Something went wrong. Check internet connection.')
