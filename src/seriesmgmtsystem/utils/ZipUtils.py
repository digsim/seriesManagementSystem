#!/usr/bin/python
# -*- coding: utf-8 -*-

################################################################################################################
# This script is a simple management system for series made of exercises and solution.                         #
# It is possible to make zipped series for moodle, a zip containing all series. Furthermore one can            #
# generate previews for one exercise/solution. Two handy functions are the make-workbook and the               #
# make-catalogue. The former one creaets a pdf containig all series, each one followed by its solution         #
# just like they were distributed. The latter one create a sort of index of all available exercises in         #
# the system. Each exercise is followed by its solution.                                                       #
#                                                                                                              #
# The structure for a new exercise should be created by using the make-new-exercise function.                  #
# For further help, please refer to the help function of the software.                                         #
# -------------------------------------------------------------------------------------------------------------#
# Author: Andreas Ruppen                                                                                       #                                                                                                                                                             #
# Licensed under the Apache License, Version 2.0 (the "License");                                              #
#   you may not use this file except in compliance with the License.                                           #
#   You may obtain a copy of the License at                                                                    #
#                                                                                                              #
#       http://www.apache.org/licenses/LICENSE-2.0                                                             #
#                                                                                                              #
#   Unless required by applicable law or agreed to in writing, software                                        #
#   distributed under the License is distributed on an "AS IS" BASIS,                                          #
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.                                   #
#   See the License for the specific language governing permissions and                                        #
#   limitations under the License.                                                                             #
################################################################################################################

import logging
import os
import zipfile
import tarfile
import subprocess
import shutil

log = logging.getLogger('seriesManagementSystem')

def myZip(directory, destZipFile, zipPrefix="."):
    """Zips a directory recursively to the destination zipfile"""
    log.debug("Zipping directory: "+directory+" to "+destZipFile)
    if len(os.listdir(directory)) == 0:
        return
    zippedDir = zipfile.ZipFile(destZipFile, 'w')
    def zipTreeWalker(args, dirname, fnames):
        theZipArch = args[0]
        root = args[1]
        prefix = args[2]
        fnames.sort()
        for file in fnames:
            file = os.path.join(dirname, file)
            archiveName = file[len(os.path.commonprefix((root, file)))+1:]
            archiveName = os.path.join(prefix, archiveName)
            if not os.path.isdir(file):
                theZipArch.write(file, archiveName)
    for root, dirs, files in os.walk(directory):
        zipTreeWalker([zippedDir, directory, zipPrefix], root, files)
    

def myTar(directory, destTarFile, tarPrefix="."):
    """Creates a tar.gz file of a directory to destTarFile"""
    def isSvn(f):
        return f.endswith(".svn")
    
    log.debug("Tar.gz - ing "+directory+" to "+destTarFile+". Using python tar")
    containingFolder = os.path.basename(destTarFile)[:os.path.basename(destTarFile).find(".")]
    tarTempName = "/tmp/tmp.tar.gz"
    files = os.listdir(directory)
    if len(files) == 0:
        return
    tarArchive = tarfile.open(tarTempName, 'w:gz')
    cwd = os.getcwd()
    os.chdir(os.path.join(cwd, directory))
    for file in files:
        tarArchive.add(file, containingFolder+"/"+file, exclude=isSvn)
    os.chdir(cwd)
    if len(tarArchive.getmembers()) == 0: 
        return
    tarArchive.close()
    
    shutil.move(tarTempName, destTarFile)
    return destTarFile

def sysTar(directory, destTarFile, tarPrefix="."):
    cwd = os.getcwd()
    log.debug("Tar.gz - ing "+directory+" to "+destTarFile+". Using system tar")
    tarTempName = "/tmp/tmp.tar.gz"
    basename = os.path.basename(directory)
    dirname = os.path.dirname(directory)
    os.chdir(os.path.join(cwd, dirname))
    subprocess.call(["tar -czf "+tarTempName+" --exclude='\.svn' "+basename], shell=True, cwd="./", stdout=open("/dev/stdout", 'w'))
    os.chdir(cwd)
    shutil.move(tarTempName, destTarFile)
        