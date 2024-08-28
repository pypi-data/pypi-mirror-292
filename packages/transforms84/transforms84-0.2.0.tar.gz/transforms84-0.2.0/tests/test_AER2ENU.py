import numpy as np
import pytest

from transforms84.transforms import AER2ENU

# https://www.lddgo.net/en/coordinate/ecef-enu


def test_ENU2AER_raise_wrong_dtype():
    AER = np.array([[3906.67536618], [2732.16708], [1519.47079847]], dtype=np.float16)
    with pytest.raises(ValueError):
        AER2ENU(AER)  # type: ignore


@pytest.mark.skip(reason="To be implemented")
def test_ENU2AER_float32_point(tolerance_float_atol):
    AER = np.array([[3906.67536618], [2732.16708], [1519.47079847]], dtype=np.float32)
    _ = AER2ENU(AER)
    ...


@pytest.mark.skip(reason="To be implemented")
def test_ENU2AER_float64_point():
    AER = np.array([[3906.67536618], [2732.16708], [1519.47079847]], dtype=np.float64)
    _ = AER2ENU(AER)
    ...


@pytest.mark.skip(reason="To be implemented")
def test_ENU2AER_float32_points(tolerance_float_atol):
    AER = np.array(
        [
            [[3906.67536618], [2732.16708], [1519.47079847]],
            [[3906.67536618], [2732.16708], [1519.47079847]],
        ],
        dtype=np.float32,
    )
    _ = AER2ENU(AER)
    ...


@pytest.mark.skip(reason="To be implemented")
def test_ENU2AER_float64_points():
    AER = np.array(
        [
            [[3906.67536618], [2732.16708], [1519.47079847]],
            [[3906.67536618], [2732.16708], [1519.47079847]],
        ],
        dtype=np.float64,
    )
    _ = AER2ENU(AER)
    ...
