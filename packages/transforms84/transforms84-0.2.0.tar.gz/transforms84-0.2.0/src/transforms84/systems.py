import numpy as np


class WGS:
    def __init__(self, a: float, b: float):
        self.a = a  # Earth semi-major axis (equatorial radius) in metres
        self.b = b  # Earth semi-minor axis (polar radius) in metres

    @property
    def mean_radius(self) -> float:
        """mean radius of ellipsoid in metres"""
        return (2 * self.a + self.b) / 3

    @property
    def e(self) -> float:
        """eccentricity (indicates the elongation of an ellipse away from a circle)"""
        out = np.sqrt(1 - (self.b**2 / self.a**2))
        assert isinstance(out, float)
        return out

    @property
    def e2(self) -> float:
        """second eccentricity squared"""
        return self.e**2 / (1 - self.e**2)

    def __eq__(self, other):
        return isinstance(other, WGS) and self.a == other.a and self.b == other.b


WGS84 = WGS(6378137.0, 6356752.314245)
