"""Setup script for the kake package."""
from setuptools import setup

setup(
    name='kake',
    version='0.1',
    description='Klinoff Application Konstruction Engine',
    author='Jooapa',
    py_modules=['kake'],
    include_package_data=True,
    package_dir={'': 'src'},
)
