import os
import setuptools

SETUPDIR = os.path.dirname(__file__)
PKGDIR = os.path.join(SETUPDIR, 'src')

with open(os.path.join(SETUPDIR, 'README.md'), 'r') as f:
    long_description = f.read()


setuptools.setup(
    name='nextcloud',
    version='0.0.2',
    author='EnterpriseyIntranet',
    description="Python wrapper for NextCloud api",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/EnterpriseyIntranet/nextcloud-API",
    packages=setuptools.find_packages(PKGDIR),
    include_package_data=True,
    install_requires=[
        'requests >= 2.0.1',
        'six'
    ],
    package_dir={'': 'src'},
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        "Operating System :: OS Independent",
    ],
)
