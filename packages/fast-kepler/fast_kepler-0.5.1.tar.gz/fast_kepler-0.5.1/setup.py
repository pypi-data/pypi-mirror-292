from setuptools import setup, Extension, find_packages
from setuptools.command.build_ext import build_ext as _build_ext
from Cython.Build import cythonize
import numpy


# Define the Cython extension
extensions = [
    Extension(
        name="fast_kepler",  # Fully qualified module name
        sources=["src/_kepler.pyx"],  # Cython source
        include_dirs=[numpy.get_include()],  # Include NumPy headers
        language="c"  # Specify C (use 'c++' if you're using C++)
    )
]


with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="fast_kepler",
    version='0.5.1',
    author="ReddTea",
    description="kepler equation solver in c for python",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    license='MIT',
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Cython",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    setup_requires=['numpy', 'cython'],
    ext_modules=cythonize(extensions, compiler_directives={'language_level': "3"}),  # Cythonize extensions
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.6",
    )