import subprocess
import sys

from setuptools import Extension


def install_packages(*requirements):
    subprocess.check_call(
        [sys.executable, "-m", "pip", "install"] + list(requirements)
    )


def get_or_install(name, version=None):
    import json
    js_packages = json.loads(
        subprocess.check_output(
            [sys.executable, "-m", "pip", "list", "--format", "json"]
        ).decode('ascii')
    )
    try:
        [package] = (
            package for package in js_packages if package['name'] == name
        )
    except ValueError:
        install_packages("%s==%s" % (name, version) if version else name)
        return version
    else:
        if version and package['version'] != version:
            install_packages("%s==%s" % (name, version))
        return package['version']


def get_long_description():
    with open('README.md') as f:
        long_description = f.read()

    try:
        import github2pypi
        return github2pypi.replace_url(
            slug='ethanmclark1/octomap_py', content=long_description
        )
    except Exception:
        return long_description


def main():
    # Ensure a compatible version of NumPy is installed
    get_or_install('numpy', '1.24.3')  # Using 1.24.3 as an example compatible version

    # Install other build dependencies
    get_or_install('cython')
    get_or_install('scikit-build')

    from Cython.Distutils import build_ext
    import numpy
    import skbuild

    ext_modules = [
        Extension(
            'octomap',
            ['octomap/octomap.pyx'],
            include_dirs=[
                'src/octomap/octomap/include',
                'src/octomap/dynamicEDT3D/include',
                numpy.get_include(),
            ],
            library_dirs=[
                'src/octomap/lib',
            ],
            libraries=[
                'dynamicedt3d',
                'octomap',
                'octomath',
            ],
            language='c++',
        )
    ]

    skbuild.setup(
        name="octomap_py",
        version="1.8.0.post12",
        author="Blake Narramore",
        author_email="blaque2pi@msn.com",
        install_requires=["numpy>=1.24.3,<1.25.0"],  # Ensuring compatible NumPy version
        extras_require={
            "example": ["glooey", "imgviz>=1.2.0", "pyglet", "trimesh[easy]"],
        },
        license="BSD",
        maintainer="Blake Narramore, Ethan Clark",
        maintainer_email="blaque2pi@msn.com, eclark715@gmail.com",
        url="https://github.com/ethanmclark1/octomap_py",
        description="Python binding of the OctoMap library.",
        long_description=get_long_description(),
        long_description_content_type="text/markdown",
        classifiers=[
            "Development Status :: 5 - Production/Stable",
            "Intended Audience :: Developers",
            "Natural Language :: English",
            "Programming Language :: Python",
            "Programming Language :: Python :: 2",
            "Programming Language :: Python :: 3",
            "Programming Language :: Python :: Implementation :: CPython",
            "Programming Language :: Python :: Implementation :: PyPy",
        ],
        ext_modules=ext_modules,
        cmdclass={"build_ext": build_ext},
        cmake_source_dir="src/octomap",
    )


if __name__ == '__main__':
    main()
