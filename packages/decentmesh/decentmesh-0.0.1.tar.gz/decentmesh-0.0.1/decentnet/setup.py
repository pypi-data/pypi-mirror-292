from setuptools import setup
from Cython.Build import cythonize

setup(
    requires=["tensorflow", "numpy", "tensorflow_addons", "cython", "tensorflow-addons","pymerkle"],
    ext_modules=cythonize("computation_fast.pyx")
)
