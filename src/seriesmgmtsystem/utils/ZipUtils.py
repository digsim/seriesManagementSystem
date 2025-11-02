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
import shutil
import subprocess
import tarfile
import typing
import zipfile

log = logging.getLogger("seriesManagementSystem")


def myZip(directory: str, destZipFile: str, zipPrefix: str = ".") -> None:
    """Zips a directory recursively to the destination zipfile"""
    log.debug("Zipping directory: " + directory + " to " + str(destZipFile))
    if len(os.listdir(directory)) == 0:
        return
    zippedDir = zipfile.ZipFile(destZipFile, "w")

    def zipTreeWalker(args: list[typing.Any], dirname: str, fnames: list[str]) -> None:
        theZipArch = args[0]
        root = args[1]
        prefix = args[2]
        fnames.sort()
        for file in fnames:
            file = os.path.join(dirname, file)
            archiveName = file[len(os.path.commonprefix((root, file))) + 1 :]
            archiveName = os.path.join(prefix, archiveName)
            if not os.path.isdir(file):
                theZipArch.write(file, archiveName)

    for root, dirs, files in os.walk(directory):
        zipTreeWalker([zippedDir, directory, zipPrefix], root, files)


def myTar(directory: str, destTarFile: str, zipPrefix: str = ".") -> str | None:
    """Creates a tar.gz file of a directory to destTarFile"""

    def isSvn(f: tarfile.TarInfo) -> tarfile.TarInfo | None:
        if f.name.endswith(".svn"):
            return None
        else:
            return f

    log.debug("Tar.gz - ing " + directory + " to " + destTarFile + ". Using python tar")
    containingFolder = os.path.basename(destTarFile)[
        : os.path.basename(destTarFile).find(".")
    ]
    tarTempName = "/tmp/tmp.tar.gz"
    files = os.listdir(directory)
    if len(files) == 0:
        return None
    cwd = os.getcwd()
    os.chdir(os.path.join(cwd, directory))
    with tarfile.open(tarTempName, "w:gz") as tarArchive:
        for file in files:
            tarArchive.add(file, containingFolder + "/" + file, filter=isSvn)
        os.chdir(cwd)
        if len(tarArchive.getmembers()) == 0:
            return None

    shutil.move(tarTempName, destTarFile)
    return destTarFile


def sysTar(directory: str, destTarFile: os.PathLike, zipPrefix: str = ".") -> None:
    cwd = os.getcwd()
    log.debug(
        "Tar.gz - ing " + directory + " to " + str(destTarFile) + ". Using system tar"
    )
    tarTempName = "/tmp/tmp.tar.gz"
    basename = os.path.basename(directory)
    dirname = os.path.dirname(directory)
    os.chdir(os.path.join(cwd, dirname))
    subprocess.call(
        ["tar -czf " + tarTempName + r" --exclude='\.svn' " + basename],
        shell=True,
        cwd="./",
        stdout=open("/dev/stdout", "w"),
    )
    os.chdir(cwd)
    shutil.move(tarTempName, destTarFile)
