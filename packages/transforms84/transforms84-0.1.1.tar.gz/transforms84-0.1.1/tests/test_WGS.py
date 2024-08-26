import numpy as np

from transforms84.systems import WGS, WGS84


def test_WGS84():
    assert np.isclose(WGS84.mean_radius, 6371008.771415)
    assert np.isclose(WGS84.e, 0.08181919084296556)
    assert np.isclose(WGS84.e2, 0.006739496742333499)
    assert WGS(6378137.0, 6356752.314245) == WGS84
