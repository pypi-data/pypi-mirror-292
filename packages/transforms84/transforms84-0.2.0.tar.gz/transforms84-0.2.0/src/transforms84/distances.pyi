import numpy.typing as npt

from . import DTYPES_SUPPORTED

def Haversine(
    rrmStart: npt.NDArray[DTYPES_SUPPORTED],
    rrmEnd: npt.NDArray[DTYPES_SUPPORTED],
    m_radius_sphere: float,
) -> npt.NDArray[DTYPES_SUPPORTED]: ...
