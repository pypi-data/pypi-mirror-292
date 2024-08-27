#!/usr/bin/env python3


import numpy as np
from lemaitre import bandpasses

def random_sensor_id(band, size):
    if 'megacam6' in band:
        return np.random.choice(np.arange(0, 36), size)
    if 'hsc' in band:
        return np.random.choice(np.arange(0, 103), size)
    if 'ztf' in band:
        return np.random.choice(np.arange(1, 65), size)
    return None


def test_check_args(nmeas=100_000):
    """
    """
    fl = bandpasses.get_filterlib()
    star = np.random.randint(131, size=nmeas)
    band = np.random.choice(fl.bandpass_names, size=nmeas)
    x = np.random.uniform(0., 3000., nmeas)
    y = np.random.uniform(0., 3000., nmeas)
    sensor_id = np.zeros(nmeas).astype(int)

    for b in np.unique(band):
        idx = band == b
        sensor_id[idx] = random_sensor_id(b, idx.sum())

    return fl, star, band, x, y, sensor_id
