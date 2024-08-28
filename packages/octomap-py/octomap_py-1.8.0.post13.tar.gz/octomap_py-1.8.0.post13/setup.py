from setuptools import setup, Extension, find_packages
from Cython.Build import cythonize
import numpy as np
import os

# Specify the paths to the OctoMap libraries and include files
octomap_include_dir = 'src/octomap/octomap/include'
dynamicedt3d_include_dir = 'src/octomap/dynamicEDT3D/include'
octomap_lib_dir = 'src/octomap/lib'

# Define the extension
extensions = [
    Extension(
        "octomap.octomap",
        ["octomap/octomap.pyx"],
        include_dirs=[
            octomap_include_dir,
            dynamicedt3d_include_dir,
            np.get_include(),
        ],
        library_dirs=[octomap_lib_dir],
        libraries=['octomap', 'octomath', 'dynamicedt3d'],
        language='c++',
        extra_compile_args=['-std=c++11'],
        extra_link_args=['-Wl,-rpath,$ORIGIN/../src/octomap/lib'],
    )
]

def get_long_description():
    with open('README.md', 'r', encoding='utf-8') as f:
        return f.read()

setup(
    name="octomap_py",
    version="1.8.0.post13",
    author="Blake Narramore",
    author_email="blaque2pi@msn.com",
    description="Python binding of the OctoMap library.",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    url="https://github.com/ethanmclark1/octomap_py",
    packages=find_packages(),
    ext_modules=cythonize(extensions),
    package_data={
        'octomap': ['*.so*', '*.dylib*', '*.dll'],
    },
    include_package_data=True,
    install_requires=[
        'numpy>=1.24.3,<1.25.0',
    ],
    extras_require={
        "example": ["glooey", "imgviz>=1.2.0", "pyglet", "trimesh[easy]"],
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: C++",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Visualization",
    ],
    python_requires='>=3.6',
    license="BSD",
)