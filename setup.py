#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from setuptools import setup, find_packages
from distutils.command.install_data import install_data
from pip.req import parse_requirements


cmdclass = {'install_data': install_data}
data_files = [('/etc/AdNITC/', ['etc/adnitc.conf', 'etc/logging.conf']), ('/usr/local/etc/bash_completion.d/', ['etc/adnitc-completion.bash'])]
# parse_requirements() returns generator of pip.req.InstallRequirement objects
install_reqs = parse_requirements('requirements.txt', session=False)
reqs = [str(ir.req) for ir in install_reqs]



# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="seriesmgmtsystem",
    version="1.0.dev0",
    author="Andreas Ruppen",
    author_email="andreas.ruppen@gmail.com",
    description="Manages Series",
    license="Apache",
    keywords="students series",
    url="https://github.com/digsim/seriesManagementSystem",
    packages=find_packages(exclude=['contrib', 'docs', '*.tests*']),
    entry_points={
        'console_scripts': [
            'seriesManagementSystem=seriesmgmtsystem.main:main',
        ],
    },
    cmdclass=cmdclass,
    #data_files=data_files,
    #package_data = {'etc':'**/*'},
    include_package_data = True,
    install_requires=reqs,
    test_suite='nose.collector',
    tests_require=['nose'],
    dependency_links=["git+https://github.com/svpino/rfeed.git#egg=rfeed"],
    long_description=read('README.rst'),
    zip_safe=True,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        'Intended Audience :: Developers',
        "Topic :: Utilities",
        "License :: OSI Approved :: Apache Software License",
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
    platforms='any',
)
