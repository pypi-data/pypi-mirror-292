from setuptools import setup
from setuptools.extension import Extension
from Cython.Build import cythonize
import numpy

extensions = [
    Extension(
        "agox.models.GPR.priors.repulsive", ["agox/models/GPR/priors/repulsive.pyx"], include_dirs=[numpy.get_include()]
    ),
    Extension(
        "agox.models.descriptors.fingerprint_cython.angular_fingerprintFeature_cy",
        ["agox/models/descriptors/fingerprint_cython/angular_fingerprintFeature_cy.pyx"],
        include_dirs=[numpy.get_include()],
    ),
]

setup(
    ext_modules=cythonize(extensions),
)