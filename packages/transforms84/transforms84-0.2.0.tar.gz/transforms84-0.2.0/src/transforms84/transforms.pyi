import numpy.typing as npt

from . import DTYPES_SUPPORTED

def geodetic2ECEF(
    rrmLLA: npt.NDArray[DTYPES_SUPPORTED],
    m_semi_major_axis: float,
    m_semi_minor_axis: float,
) -> npt.NDArray[DTYPES_SUPPORTED]: ...
def ECEF2geodetic(
    mmmXYZ: npt.NDArray[DTYPES_SUPPORTED],
    m_semi_major_axis: float,
    m_semi_minor_axis: float,
) -> npt.NDArray[DTYPES_SUPPORTED]: ...
def ECEF2ENU(
    rrmLLA_local_origin: npt.NDArray[DTYPES_SUPPORTED],
    mmmXYZ_target: npt.NDArray[DTYPES_SUPPORTED],
    m_semi_major_axis: float,
    m_semi_minor_axis: float,
) -> npt.NDArray[DTYPES_SUPPORTED]: ...
def ENU2ECEF(
    rrmLLA_local_origin: npt.NDArray[DTYPES_SUPPORTED],
    mmmXYZ_local: npt.NDArray[DTYPES_SUPPORTED],
    m_semi_major_axis: float,
    m_semi_minor_axis: float,
) -> npt.NDArray[DTYPES_SUPPORTED]: ...
def ENU2AER(mmmENU: npt.NDArray[DTYPES_SUPPORTED]) -> npt.NDArray[DTYPES_SUPPORTED]: ...
def AER2ENU(rrmAER: npt.NDArray[DTYPES_SUPPORTED]) -> npt.NDArray[DTYPES_SUPPORTED]: ...
