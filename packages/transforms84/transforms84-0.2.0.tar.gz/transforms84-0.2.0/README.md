# transforms84
![PyPI - Version](https://img.shields.io/pypi/v/transforms84)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/transforms84)
![Codecov](https://img.shields.io/codecov/c/gh/Stoops-ML/transforms84)
![PyPI - License](https://img.shields.io/pypi/l/transforms84)

Small geographic coordinate systems Python library with a few additional helper functions.

This package focuses on:
1. Performance
2. Input and output coordinates of ideal mathematical shapes. Ideally, all coordinates should be of shapes (3,1) or (nPoints,3,1), but shapes (3,) and (nPoints,3) are supported too.
3. Functions that adapt to differing input matrices shapes: one-to-one, many-to-many and one-to-many points. See [below](#many-to-many--one-to-many) for an example.

## Installation
`pip install transforms84`

## Operations
### Transformations
The following transformations have been implemented:
- geodetic &rarr; ECEF
- ECEF &rarr; geodetic
- ECEF &rarr; ENU
- ENU &rarr; ECEF
- ENU &rarr; AER
- AER &rarr; ENU

### Distances
The following distance formulae have been implemented:
- Haversine

### Helpers
The following functions have been implemented:
- Angular difference (smallest and largest)
- [rad, rad, X] &rarr; [deg, deg, X]
- [deg, deg, X] &rarr; [rad, rad, X]

## Examples
See the Jupyter notebooks in [examples](examples) to see how to use the transform84. Run `pip install transforms84[examples]` to run the examples locally.

### Many-to-many & one-to-many
The `transforms.ECEF2ENU` transformation accepts same and differing matrix shape sizes. Below showcases the many-to-many method where three target points, `rrm_target`, in the geodetic coordinate system ([WGS84](https://en.wikipedia.org/wiki/World_Geodetic_System)) are transformed to the local ENU coordinate system about the point `rrm_local`, where both matrices are of shape (3, 3, 1):
```
>> import numpy as np
>> from transforms84.systems import WGS84
>> from transforms84.helpers import DDM2RRM
>> from transforms84.transforms import ECEF2ENU, geodetic2ECEF

>> rrm_local = DDM2RRM(np.array([[[30], [31], [0]], [[30], [31], [0]], [[30], [31], [0]]], dtype=np.float64))  # convert each point from [deg, deg, X] to [rad, rad, X]
>> rrm_target = DDM2RRM(np.array([[[31], [32], [0]], [[31], [32], [0]], [[31], [32], [0]]], dtype=np.float64))
>> ECEF2ENU(rrm_local, geodetic2ECEF(rrm_target, WGS84.a, WGS84.b), WGS84.a, WGS84.b)  # geodetic2ECEF -> ECEF2ENU
array([[[ 4.06379074e+01],
        [-6.60007585e-01],
        [ 1.46643956e+05]],

       [[ 4.06379074e+01],
        [-6.60007585e-01],
        [ 1.46643956e+05]],

       [[ 4.06379074e+01],
        [-6.60007585e-01],
        [ 1.46643956e+05]]])
```

We can achieve the same result using the one-to-many method with a single local point of shape (3, 1):
```
>> rrm_local = DDM2RRM(np.array([[30], [31], [0]], dtype=np.float64))
>> ECEF2ENU(rrm_local, geodetic2ECEF(rrm_target, WGS84.a, WGS84.b), WGS84.a, WGS84.b)
array([[[ 4.06379074e+01],
        [-6.60007585e-01],
        [ 1.46643956e+05]],

       [[ 4.06379074e+01],
        [-6.60007585e-01],
        [ 1.46643956e+05]],

       [[ 4.06379074e+01],
        [-6.60007585e-01],
        [ 1.46643956e+05]]])
```

## Contributing
PRs are always welcome and appreciated! Please install the pre-commit hooks before making commits.
