import os
from distutils.core import setup
from setuptools import find_packages

prog_dir = os.path.dirname(os.path.realpath(__file__))

with open('%s/sampletodo/VERSION' % prog_dir) as f:
  version = f.read().strip()

with open('%s/requirements.txt' % prog_dir) as f:
  requirements = f.read().splitlines()

with open('%s/test-requirements.txt' % prog_dir) as f:
  test_requirements = f.read().splitlines()

with open('%s/sampletodo/VERSION' % prog_dir) as f:
  version = f.read().strip()

setup(
    # Application name:
    name="sampletodo",

    # Version number:
    version=version,
    #version='1.0.0',

    # Application author details:
    author="Saurabh Hirani",
    author_email="saurabh.hirani@autodesk.com",

    # Packages
    packages=find_packages(),

    # Include additional files into the package
    include_package_data=True,

    # license="LICENSE.txt",
    description="Sample python todo app",

    entry_points = {
      'console_scripts': [
        'sampletodo = sampletodo.run:main'
      ]
    },

    # Dependent packages (distributions)
    install_requires=requirements,

    # run tests suite by
    test_suite='nose.collector',

    # Install test requiremenets
    tests_require=test_requirements

)
