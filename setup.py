"""
Setup script

Usage :
    python setup.py build
    python setup.py install

For repository admin:
    python setup.py publish

For testing:
    test.sh
"""
import os
import sys
from setuptools import setup, find_packages

# 'setup.py publish' shortcut.
if sys.argv[-1] == 'publish':
    # see https://twine.readthedocs.io/en/latest/
    os.system('%s %s sdist bdist_wheel' % (sys.executable, sys.argv[0]))
    os.system('twine upload dist/*')
    sys.exit()

setup(
    # see setup.cfg
    # some variables are defined here for retro compat with setuptools >= 33
    package_dir = {'': 'src'},
    packages=find_packages(where=r'./src'),
    long_description_content_type = 'text/markdown'
)
