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
    os.system('rm -rf dist build')
    os.system('python %s sdist bdist_wheel' % (sys.argv[0]))
    os.system('python3 %s sdist bdist_wheel' % (sys.argv[0]))
    os.system('twine upload dist/*')
    sys.exit()

setup(
    # see setup.cfg
    # some variables are defined here for retro compat with setuptools >= 33
    package_dir = {'': 'src'},
    packages=find_packages(where=r'./src'),
    long_description_content_type = 'text/x-rst'
)
