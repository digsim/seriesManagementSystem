#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from setuptools import setup, find_packages
from distutils.command.install_data import install_data


def walk_subpkg(name):
    data_files = []
    package_dir = 'SMS'
    for parent, dirs, files in os.walk(os.path.join(package_dir, name)):
        sub_dir = os.sep.join(parent.split(os.sep)[1:])  # remove package_dir from the path
        for f in files:
            data_files.append(os.path.join(sub_dir, f))
    return data_files



scripts = ['bin/seriesManagementSystem']
cmdclass = {'install_data': install_data}
data_files = [('/etc/SeriesManagementSystem/', ['etc/lecture.cfg', 'etc/logging.conf']), ('/usr/local/etc/bash_completion.d/', ['etc/serieManagementSystem-completion.bash'])]
package_data = {'xwot': ['examples/*'],
                "xwot": [] + walk_subpkg('REST-Server-Skeleton/') + walk_subpkg('NM_REST-Server-Skeleton/') + walk_subpkg('examples/')}

# except IndexError: pass

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="Series Management System",
    version="1.1",
    author="Andreas Ruppen",
    author_email="andreas.ruppen@gmail.com",
    description="Manages Series",
    license="LGPL",
    keywords="students series",
    url="http://diufpc46.unifr.ch/projects/projects/SMS",
    packages=find_packages(),
#    package_data=package_data,
    scripts=scripts,
    cmdclass=cmdclass,
    data_files=data_files,
#    install_requires=['colorama'],
    long_description=read('README.md'),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        'Intended Audience :: Developers',
        "Topic :: Utilities",
        "License :: OSI Approved :: Lesser GPL License",
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Programming Language :: Python',
    ],
    platforms='any',
)
