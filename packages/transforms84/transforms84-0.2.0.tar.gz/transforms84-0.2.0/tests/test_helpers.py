import numpy as np

from transforms84.helpers import (
    DDM2RRM,
    RRM2DDM,
    deg_angular_difference,
    deg_angular_differences,
    rad_angular_difference,
    rad_angular_differences,
)


def test_XXM2YYM_one_point_64():
    rrm_point = np.array([[30], [31], [0]], dtype=np.float64)
    out = DDM2RRM(RRM2DDM(rrm_point))
    assert np.all(np.isclose(rrm_point, out))
    assert rrm_point.dtype == out.dtype


def test_XXM2YYM_one_point_32():
    rrm_point = np.array([[30], [31], [0]], dtype=np.float32)
    out = DDM2RRM(RRM2DDM(rrm_point))
    assert np.all(np.isclose(rrm_point, out))
    assert rrm_point.dtype == out.dtype


def test_XXM2YYM_multiple_points_64():
    rrm_point = np.array([[[30], [31], [0]], [[30], [31], [0]]], dtype=np.float64)
    out = DDM2RRM(RRM2DDM(rrm_point))
    assert np.all(np.isclose(rrm_point, out))
    assert rrm_point.dtype == out.dtype


def test_XXM2YYM_multiple_points_32():
    rrm_point = np.array([[[30], [31], [0]], [[30], [31], [0]]], dtype=np.float32)
    out = DDM2RRM(RRM2DDM(rrm_point))
    assert np.all(np.isclose(rrm_point, out))
    assert rrm_point.dtype == out.dtype


def test_deg_angular_differences_smallest_angle():
    for diff_v in range(0, 179):
        diff = np.ones((1000,), dtype=np.float32) * diff_v
        assert np.all(diff == deg_angular_differences(diff, diff + diff_v, True))


def test_deg_angular_differences_largest_angle():
    for diff_v in range(0, 1000):
        diff = np.ones((1000,), dtype=np.float32) * diff_v
        assert np.all(
            diff % 360.0 == deg_angular_differences(diff, diff + diff_v, False)
        )


def test_deg_angular_difference_smallest_angle():
    for diff in range(0, 179):
        for i in range(1000):
            assert diff == deg_angular_difference(diff * i, diff * (i + 1), True)


def test_deg_angular_difference_largest_angle():
    for diff in range(0, 1000):
        for i in range(1000):
            assert diff % 360.0 == deg_angular_difference(
                diff * i, diff * (i + 1), False
            )


def test_rad_angular_differences_smallest_angle():
    for diff_v in range(0, 179):
        diff_v = np.deg2rad(diff_v)
        diff = np.ones((1000,), dtype=np.float32) * diff_v
        assert np.all(diff == rad_angular_differences(diff, diff + diff_v, True))


def test_rad_angular_differences_largest_angle():
    for diff_v in range(0, 1000):
        diff_v = np.deg2rad(diff_v)
        diff = np.ones((1000,), dtype=np.float32) * diff_v
        assert np.all(
            diff % (2 * np.pi) == rad_angular_differences(diff, diff + diff_v, False)
        )


def test_rad_angular_difference_smallest_angle():
    for diff in range(0, 179):
        for i in range(1000):
            diff_v = np.deg2rad(diff)
            assert np.isclose(
                diff_v, rad_angular_difference(diff_v * i, diff_v * (i + 1), True)
            )


def test_rad_angular_difference_largest_angle():
    for diff in range(0, 1000):
        for i in range(1000):
            diff_v = np.deg2rad(diff) % (2 * np.pi)
            assert np.isclose(
                diff_v % (2 * np.pi),
                rad_angular_difference(diff_v * i, diff_v * (i + 1), False),
            )
