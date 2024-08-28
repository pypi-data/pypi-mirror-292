import numpy as np
import pytest

from transforms84.transforms import ENU2AER

# https://www.lddgo.net/en/coordinate/ecef-enu


def test_ENU2AER_raise_wrong_dtype():
    ENU = np.array([[3906.67536618], [2732.16708], [1519.47079847]], dtype=np.float16)
    with pytest.raises(ValueError):
        ENU2AER(ENU)  # type: ignore


@pytest.mark.skip(reason="To be implemented")
def test_ENU2AER_float32_point(tolerance_float_atol):
    ENU = np.array([[3906.67536618], [2732.16708], [1519.47079847]], dtype=np.float32)
    _ = ENU2AER(ENU)
    ...


@pytest.mark.skip(reason="To be implemented")
def test_ENU2AER_float64_point():
    ENU = np.array([[3906.67536618], [2732.16708], [1519.47079847]], dtype=np.float64)
    _ = ENU2AER(ENU)
    ...


@pytest.mark.skip(reason="To be implemented")
def test_ENU2AER_float32_points(tolerance_float_atol):
    ENU = np.array(
        [
            [[3906.67536618], [2732.16708], [1519.47079847]],
            [[3906.67536618], [2732.16708], [1519.47079847]],
        ],
        dtype=np.float32,
    )
    _ = ENU2AER(ENU)
    ...


@pytest.mark.skip(reason="To be implemented")
def test_ENU2AER_float64_points():
    ENU = np.array(
        [
            [[3906.67536618], [2732.16708], [1519.47079847]],
            [[3906.67536618], [2732.16708], [1519.47079847]],
        ],
        dtype=np.float64,
    )
    _ = ENU2AER(ENU)
    ...
