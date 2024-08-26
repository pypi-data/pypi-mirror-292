import numpy as np
from setuptools import Extension, setup

setup(
    ext_modules=[
        Extension(
            "transforms84.transforms",
            sources=["transforms.c"],
            include_dirs=[np.get_include()],
        ),
        Extension(
            "transforms84.distances",
            sources=["distances.c"],
            include_dirs=[np.get_include()],
        ),
        Extension(
            "transforms84.helpers",
            sources=["helpers.c"],
            include_dirs=[np.get_include()],
        ),
    ],
)
