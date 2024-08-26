import numpy as np
import pytest

from transforms84.systems import WGS84
from transforms84.transforms import ECEF2geodetic


def test_ECEF2geodetic_raise_wrong_dtype():
    in_arr = np.array([[5010306], [2336344], [3170376.2]], dtype=np.float16)
    with pytest.raises(ValueError):
        ECEF2geodetic(in_arr, WGS84.a, WGS84.b)  # type: ignore


def test_ECEF2geodetic_raise_wrong_size():
    in_arr = np.array([[5010306], [2336344], [3170376.2], [1]], dtype=np.float64)
    with pytest.raises(ValueError):
        ECEF2geodetic(in_arr, WGS84.a, WGS84.b)


def test_ECEF2geodetic_float32_point(tolerance_float_atol):
    in_arr = np.array([[5010306], [2336344], [3170376.2]], dtype=np.float32)
    out = ECEF2geodetic(in_arr, WGS84.a, WGS84.b)
    assert np.isclose(out[0, 0], np.deg2rad(30))
    assert np.isclose(out[1, 0], np.deg2rad(25))
    assert np.isclose(out[2, 0], 5, atol=tolerance_float_atol)


def test_ECEF2geodetic_float64_point(tolerance_double_atol):
    in_arr = np.array([[5010306], [2336344], [3170376.2]], dtype=np.float64)
    out = ECEF2geodetic(in_arr, WGS84.a, WGS84.b)
    assert np.isclose(out[0, 0], np.deg2rad(30))
    assert np.isclose(out[1, 0], np.deg2rad(25))
    assert np.isclose(out[2, 0], 5, atol=tolerance_double_atol)


def test_ECEF2geodetic_float32_points(tolerance_float_atol):
    in_arr = np.array(
        [
            [[5010306], [2336344], [3170376.2]],
            [[5010306], [2336344], [3170376.2]],
        ],
        dtype=np.float32,
    )
    out = ECEF2geodetic(in_arr, WGS84.a, WGS84.b)
    assert np.all(np.isclose(out[:, 0, 0], np.deg2rad(30)))
    assert np.all(np.isclose(out[:, 1, 0], np.deg2rad(25)))
    assert np.all(np.isclose(out[:, 2, 0], 5, atol=tolerance_float_atol))


def test_ECEF2geodetic_float64_points(tolerance_double_atol):
    in_arr = np.array(
        [
            [[5010306], [2336344], [3170376.2]],
            [[5010306], [2336344], [3170376.2]],
        ],
        dtype=np.float64,
    )
    out = ECEF2geodetic(in_arr, WGS84.a, WGS84.b)
    assert np.all(np.isclose(out[:, 0, 0], np.deg2rad(30)))
    assert np.all(np.isclose(out[:, 1, 0], np.deg2rad(25)))
    assert np.all(np.isclose(out[:, 2, 0], 5, atol=tolerance_double_atol))
