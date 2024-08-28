import pytest


@pytest.fixture
def tolerance_float_atol() -> float:
    return 0.2


@pytest.fixture
def tolerance_double_atol() -> float:
    return 0.01
