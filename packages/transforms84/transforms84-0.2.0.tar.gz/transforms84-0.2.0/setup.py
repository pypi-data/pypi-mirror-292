import numpy as np
from setuptools import Extension, setup

setup(
    ext_modules=[
        Extension(
            "transforms84.transforms",
            sources=["include/transforms.c"],
            include_dirs=[np.get_include()],
        ),
        Extension(
            "transforms84.distances",
            sources=["include/distances.c"],
            include_dirs=[np.get_include()],
        ),
        Extension(
            "transforms84.helpers",
            sources=["include/helpers.c"],
            include_dirs=[np.get_include()],
        ),
    ],
)
