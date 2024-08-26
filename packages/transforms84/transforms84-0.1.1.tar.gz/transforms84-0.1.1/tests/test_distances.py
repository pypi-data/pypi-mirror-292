import numpy as np
import pytest

from transforms84.distances import Haversine
from transforms84.systems import WGS84

# https://calculator.academy/haversine-distance-calculator/


def test_Haersine_raise_wrong_dtype():
    rrm_start = np.array([[np.deg2rad(33)], [np.deg2rad(34)], [0]], dtype=np.float16)
    with pytest.raises(ValueError):
        Haversine(rrm_start, rrm_start, WGS84.mean_radius)  # type: ignore


def test_Haersine_raise_wrong_size():
    rrm_start = np.array(
        [[np.deg2rad(33)], [np.deg2rad(34)], [0], [1]], dtype=np.float32
    )
    with pytest.raises(ValueError):
        Haversine(rrm_start, rrm_start, WGS84.mean_radius)


def test_Haversine_float():
    rrm_start = np.array([[np.deg2rad(33)], [np.deg2rad(34)], [0]], dtype=np.float32)
    rrm_end = np.array([[np.deg2rad(32)], [np.deg2rad(38)], [0]], dtype=np.float32)
    assert np.isclose(
        Haversine(rrm_start, rrm_end, WGS84.mean_radius), 391225.574516907
    )
    assert np.isclose(
        Haversine(rrm_end, rrm_start, WGS84.mean_radius), 391225.574516907
    )


def test_Haversine_with_height_float():
    rrm_start_with_height = np.array(
        [[np.deg2rad(33)], [np.deg2rad(34)], [100000]], dtype=np.float32
    )
    rrm_start = np.array([[np.deg2rad(33)], [np.deg2rad(34)], [0]], dtype=np.float32)
    rrm_end = np.array([[np.deg2rad(32)], [np.deg2rad(38)], [0]], dtype=np.float32)
    assert np.isclose(
        Haversine(rrm_start_with_height, rrm_end, WGS84.mean_radius), 391225.574516907
    )
    assert np.isclose(
        Haversine(rrm_start_with_height, rrm_end, WGS84.mean_radius),
        Haversine(rrm_start, rrm_end, WGS84.mean_radius),
    )
    assert np.isclose(
        Haversine(rrm_start, rrm_end, WGS84.mean_radius), 391225.574516907
    )
    assert np.isclose(
        Haversine(rrm_end, rrm_start_with_height, WGS84.mean_radius), 391225.574516907
    )
    assert np.isclose(
        Haversine(rrm_end, rrm_start, WGS84.mean_radius), 391225.574516907
    )
    assert np.isclose(
        Haversine(rrm_start, rrm_end, WGS84.mean_radius),
        Haversine(rrm_start_with_height, rrm_end, WGS84.mean_radius),
    )


def test_Haversine_double():
    rrm_start = np.array([[np.deg2rad(33)], [np.deg2rad(34)], [0]], dtype=np.float64)
    rrm_end = np.array([[np.deg2rad(32)], [np.deg2rad(38)], [0]], dtype=np.float64)
    assert np.isclose(
        Haversine(rrm_start, rrm_end, WGS84.mean_radius), 391225.574516907
    )
    assert np.isclose(
        Haversine(rrm_end, rrm_start, WGS84.mean_radius), 391225.574516907
    )


def test_Haversine_with_height_double():
    rrm_start_with_height = np.array(
        [[np.deg2rad(33)], [np.deg2rad(34)], [100000]], dtype=np.float64
    )
    rrm_start = np.array([[np.deg2rad(33)], [np.deg2rad(34)], [0]], dtype=np.float64)
    rrm_end = np.array([[np.deg2rad(32)], [np.deg2rad(38)], [0]], dtype=np.float64)
    assert np.isclose(
        Haversine(rrm_start_with_height, rrm_end, WGS84.mean_radius), 391225.574516907
    )
    assert np.isclose(
        Haversine(rrm_start_with_height, rrm_end, WGS84.mean_radius),
        Haversine(rrm_start, rrm_end, WGS84.mean_radius),
    )
    assert np.isclose(
        Haversine(rrm_start, rrm_end, WGS84.mean_radius), 391225.574516907
    )
    assert np.isclose(
        Haversine(rrm_end, rrm_start_with_height, WGS84.mean_radius), 391225.574516907
    )
    assert np.isclose(
        Haversine(rrm_end, rrm_start, WGS84.mean_radius), 391225.574516907
    )
    assert np.isclose(
        Haversine(rrm_start, rrm_end, WGS84.mean_radius),
        Haversine(rrm_start_with_height, rrm_end, WGS84.mean_radius),
    )
