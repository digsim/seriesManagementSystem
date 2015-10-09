#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from setuptools import setup, find_packages
from distutils.command.install_data import install_data
from pip.req import parse_requirements

def walk_subpkg(name):
    data_files = []
    package_dir = 'SMS'
    for parent, dirs, files in os.walk(os.path.join(package_dir, name)):
        sub_dir = os.sep.join(parent.split(os.sep)[1:])  # remove package_dir from the path
        for f in files:
            data_files.append(os.path.join(sub_dir, f))
    return data_files


cmdclass = {'install_data': install_data}
data_files = [('/etc/SeriesManagementSystem/', ['etc/logging.conf']), ('/usr/local/etc/bash_completion.d/', ['etc/serieManagementSystem-completion.bash'])]
package_data = {'SMS': [] + walk_subpkg('data/')}
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
    name="seriesManagementSystem",
    version="1.1.6",
    author="Andreas Ruppen",
    author_email="andreas.ruppen@gmail.com",
    description="Manages Series",
    license="Apache",
    keywords="students series",
    url="https://github.com/digsim/seriesManagementSystem",
    packages=find_packages(exclude=['contrib', 'docs', 'tests*']),
    package_data = package_data,
    entry_points={
        'console_scripts': [
            'seriesManagementSystem=SMS:main',
        ],
    },
    cmdclass=cmdclass,
    data_files=data_files,
    install_requires=reqs,
    long_description=read('README.md'),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        'Intended Audience :: Education',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Science/Research',
        "Topic :: Utilities",
        'Topic :: Education',
        'Topic :: Software Development :: Compilers',
        "License :: OSI Approved :: Apache Software License",
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX',
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
