import numpy as np
import pytest

from transforms84.systems import WGS84
from transforms84.transforms import geodetic2ECEF


def test_geodetic2ECEF_raise_wrong_dtype():
    in_arr = np.array([[np.deg2rad(30)], [np.deg2rad(25)], [5]], dtype=np.float16)
    with pytest.raises(ValueError):
        geodetic2ECEF(in_arr, WGS84.a, WGS84.b)  # type: ignore


def test_geodetic2ECEF_raise_wrong_size():
    in_arr = np.array([[np.deg2rad(30)], [np.deg2rad(25)], [5], [10]], dtype=np.float64)
    with pytest.raises(ValueError):
        geodetic2ECEF(in_arr, WGS84.a, WGS84.b)


def test_geodetic2ECEF_float32_point():
    in_arr = np.array([[np.deg2rad(30)], [np.deg2rad(25)], [5]], dtype=np.float32)
    out = geodetic2ECEF(in_arr, WGS84.a, WGS84.b)
    assert np.all(np.isclose(out[0, 0], 5010302.11))
    assert np.all(np.isclose(out[1, 0], 2336342.24))
    assert np.all(np.isclose(out[2, 0], 3170373.78))


def test_geodetic2ECEF_float64_point():
    in_arr = np.array([[np.deg2rad(30)], [np.deg2rad(25)], [5]], dtype=np.float64)
    out = geodetic2ECEF(in_arr, WGS84.a, WGS84.b)
    assert np.all(np.isclose(out[0, 0], 5010302.11))
    assert np.all(np.isclose(out[1, 0], 2336342.24))
    assert np.all(np.isclose(out[2, 0], 3170373.78))


def test_geodetic2ECEF_float32_points():
    in_arr = np.array(
        [
            [[np.deg2rad(30)], [np.deg2rad(25)], [5]],
            [[np.deg2rad(30)], [np.deg2rad(25)], [5]],
        ],
        dtype=np.float32,
    )
    out = geodetic2ECEF(in_arr, WGS84.a, WGS84.b)
    assert np.all(np.isclose(out[:, 0, 0], 5010302.11))
    assert np.all(np.isclose(out[:, 1, 0], 2336342.24))
    assert np.all(np.isclose(out[:, 2, 0], 3170373.78))


def test_geodetic2ECEF_float64_points(tolerance_double_atol):
    in_arr = np.array(
        [
            [[np.deg2rad(30)], [np.deg2rad(25)], [5]],
            [[np.deg2rad(30)], [np.deg2rad(25)], [5]],
        ],
        dtype=np.float64,
    )
    out = geodetic2ECEF(in_arr, WGS84.a, WGS84.b)
    assert np.all(np.isclose(out[:, 0, 0], 5010302.11))
    assert np.all(np.isclose(out[:, 1, 0], 2336342.24))
    assert np.all(np.isclose(out[:, 2, 0], 3170373.78))
