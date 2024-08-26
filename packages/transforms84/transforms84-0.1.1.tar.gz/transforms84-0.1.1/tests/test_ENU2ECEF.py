import numpy as np
import pytest

from transforms84.systems import WGS84
from transforms84.transforms import ENU2ECEF

# https://www.lddgo.net/en/coordinate/ecef-enu


def test_ENU2ECEF_raise_wrong_dtype():
    XYZ = np.array([[3906.67536618], [2732.16708], [1519.47079847]], dtype=np.float16)
    ref_point = np.array([[5010306], [2336344], [3170376.2]], dtype=np.float16)
    with pytest.raises(ValueError):
        ENU2ECEF(ref_point, XYZ, WGS84.a, WGS84.b)  # type: ignore


def test_ENU2ECEF_raise_same_dtype():
    XYZ = np.array([[3906.67536618], [2732.16708], [1519.47079847]], dtype=np.float32)
    ref_point = np.array([[5010306], [2336344], [3170376.2]], dtype=np.float64)
    with pytest.raises(ValueError):
        ENU2ECEF(ref_point, XYZ, WGS84.a, WGS84.b)


def test_ENU2ECEF_raise_wrong_size():
    XYZ = np.array([[3906.67536618], [2732.16708], [1519.47079847]], dtype=np.float32)
    ref_point = np.array([[5010306], [2336344], [3170376.2], [1]], dtype=np.float64)
    with pytest.raises(ValueError):
        ENU2ECEF(ref_point, XYZ, WGS84.a, WGS84.b)
    with pytest.raises(ValueError):
        ENU2ECEF(XYZ, ref_point, WGS84.a, WGS84.b)


def test_ENU2ECEF_float32_point(tolerance_float_atol):
    XYZ = np.array(
        [[1901.5690521235], [5316.9485968901], [-6378422.76482545]], dtype=np.float32
    )
    ref_point = np.array([[0.1], [0.2], [5000]], dtype=np.float32)
    out = ENU2ECEF(ref_point, XYZ, WGS84.a, WGS84.b)
    assert np.isclose(out[0, 0], 3906.67536618, atol=tolerance_float_atol)
    assert np.isclose(out[1, 0], 2732.16708, atol=tolerance_float_atol)
    assert np.isclose(out[2, 0], 1519.47079847, atol=tolerance_float_atol)


def test_ENU2ECEF_float64_point():
    XYZ = np.array(
        [[1901.5690521235], [5316.9485968901], [-6378422.76482545]], dtype=np.float64
    )
    ref_point = np.array([[0.1], [0.2], [5000]], dtype=np.float64)
    out = ENU2ECEF(ref_point, XYZ, WGS84.a, WGS84.b)
    assert np.isclose(out[0, 0], 3906.67536618)
    assert np.isclose(out[1, 0], 2732.16708)
    assert np.isclose(out[2, 0], 1519.47079847)


def test_ENU2ECEF_float32_points(tolerance_float_atol):
    XYZ = np.array(
        [
            [[1901.5690521235], [5316.9485968901], [-6378422.76482545]],
            [[1901.5690521235], [5316.9485968901], [-6378422.76482545]],
        ],
        dtype=np.float32,
    )
    ref_point = np.array(
        [[[0.1], [0.2], [5000]], [[0.1], [0.2], [5000]]], dtype=np.float32
    )
    out = ENU2ECEF(ref_point, XYZ, WGS84.a, WGS84.b)
    assert np.all(np.isclose(out[:, 0, 0], 3906.67536618, atol=tolerance_float_atol))
    assert np.all(np.isclose(out[:, 1, 0], 2732.16708, atol=tolerance_float_atol))
    assert np.all(np.isclose(out[:, 2, 0], 1519.47079847, atol=tolerance_float_atol))


def test_ENU2ECEF_float64_points():
    XYZ = np.array(
        [
            [[1901.5690521235], [5316.9485968901], [-6378422.76482545]],
            [[1901.5690521235], [5316.9485968901], [-6378422.76482545]],
        ],
        dtype=np.float64,
    )
    ref_point = np.array(
        [[[0.1], [0.2], [5000]], [[0.1], [0.2], [5000]]], dtype=np.float64
    )
    out = ENU2ECEF(ref_point, XYZ, WGS84.a, WGS84.b)
    assert np.all(np.isclose(out[:, 0, 0], 3906.67536618))
    assert np.all(np.isclose(out[:, 1, 0], 2732.16708))
    assert np.all(np.isclose(out[:, 2, 0], 1519.47079847))
