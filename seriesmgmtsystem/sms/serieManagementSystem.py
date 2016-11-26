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
#                                                                                                              #
# Author: Andreas Ruppen                                                                                       #
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

"""
Series Management System.

Usage:
  seriesManagementSystem make-new-exercise | build-all-series | make-workbook | make-catalogue [-uktz]
  seriesManagementSystem build-serie -sSERIE [-uktz]
  seriesManagementSystem preview-exercise -eEXERCISE [-uktz]
  seriesManagementSystem preview-solution -eEXERCISE [-uktz]
  seriesManagementSystem make-new-lecture -lLECTURE [-uktz]
  seriesManagementSystem -v | --version
  seriesManagementSystem -h | --help


Options:
  -h --help     Show this screen.
  -v --version  Show version.
  -e --exercise=<exercise>  Specify the exercise to preview.
  -s --serie=<serie>  Specify the serie to build.
  -l --lecture=<lecture>  Specify the lecture to create.
  -u --updatebibtex  for updating last visited date in bibtex
  -k --keepzipped  for keeping unzipped files
  -t --keeptemp  for keeping temporary files in /tmp
  -z --dozip  for doing a zip file
"""
import sys
import os
import getopt
import shutil
import logging.config

if float(sys.version[:3])<3.0:
    import ConfigParser
else: 
    import configparser as ConfigParser
import subprocess
import pkgutil
from subprocess import STDOUT
try:
    from subprocess import DEVNULL # py3k
except ImportError:
    import os
    DEVNULL = open(os.devnull, 'wb')
from distutils.dir_util import copy_tree
from seriesmgmtsystem.utils import Utils, ZipUtils
from seriesmgmtsystem.utils.LaTeX import *

class SMS:
    def __init__(self, updateBibTex, keepUnzipped, keepTemp, doZip, _serie=-1, _exercise=-1):

        self.__log = logging.getLogger('Tube4Droid')

        self.__cwd = os.getcwd()
        self.__keepTempFiles = keepTemp
        
        self.__log.debug("\033[1;33m"+self.__cwd+"\033[0m")
        self.__exoStructure = ["code", "code/donne", "code/solution", "latex", "latex/ressources", "latex/ressources/figures", "latex/ressources/code"]
        self.__DATA_DIR = pkgutil.get_loader('seriesmgmtsystem').get_filename()
        self.__DATA_DIR = os.path.dirname(self.__DATA_DIR)
        self.__DATA_DIR = os.path.join(self.__DATA_DIR, 'data')
        smsConfig = ConfigParser.SafeConfigParser()
        self.__log.debug("Reading general configuration from lecture.cfg")
        smsConfig.read([join(self.__DATA_DIR, 'lecture.cfg'), "lecture.cfg"])
        self.__smscmoodleOutputDir = smsConfig.get("Config", "moodleOutputDir")
        self.__smscremoveUnzipped = smsConfig.getboolean("Config", "removeUnzipped") if not keepUnzipped else not keepUnzipped
        self.__smscdozipfiles = smsConfig.getboolean("Config",  "createZip") if not doZip else doZip
        self.__smscupdateBibTex = smsConfig.getboolean("Config", "updateBibTex") if not updateBibTex else updateBibTex
        self.__log.info("booleans are: "+str(self.__smscremoveUnzipped)+", "+str(self.__smscdozipfiles)+", "+str(self.__smscupdateBibTex))
        self.__smscopencmd = smsConfig.get("Config", "opencmd")
        self.__smcsdebuglevel = smsConfig.getint("Config", "debugLevel")
        if smsConfig.has_option("Config", "addClearPage"):
            self.__smscaddClearPage = smsConfig.getboolean("Config", "addClearPage")
        else:
            self.__smscaddClearPage = False
        self.__usepdftk = smsConfig.getboolean("Config", "usepdftk")
        self.__exoDirName = smsConfig.get("Config", "exoDirName")
        self.__seriesConfigDir = smsConfig.get("Config", "seriesConfigDir")
        self.__outputDir = smsConfig.get("Config", "outputDir")
        self.__smscname = smsConfig.get("Lecture", "name")
        self.__smsclecturer = smsConfig.get("Lecture", "lecturer")
        self.__smscyear = smsConfig.get("Lecture", "year")
        self.__smscexercisetext = smsConfig.get("Lecture", "exercisetext")
        self.__smscsolutiontext = smsConfig.get("Lecture", "solutiontext")
        self.__smsccontenttext = smsConfig.get("Lecture", "contenttext")
        self.__smscheadertitle = smsConfig.get("Lecture", "headertitle")
        self.__smscbibtex = smsConfig.get("Lecture", "bibtex")
        self.__noCiteList = smsConfig.get("Lecture", "nocite").split(",")
        self.__smscunilogo = smsConfig.get("Logo", "unilogo")
        self.__smscgroupelogo = smsConfig.get("Logo", "groupelogo")
        self.__smscpdfkeyword = smsConfig.get("PDF", "pdfkeyword")
        self.__smscpdftitle = smsConfig.get("PDF", "pdftitle")
        self.__smscpdfauthor = smsConfig.get("PDF", "pdfauthor")
        self.__latex_error_messages = (
                                "Type X to quit or <RETURN> to proceed",
                                "! Undefined control sequence.",
                                "? ",
                                "Type  H <return>  for immediate help.",
                                "Enter file name: ",
                                "or enter new name. (Default extension: sty)"
                                )
        self.__latex_recompile_messages = (
                                    "recompile ",
                                    "re-run ",
                                    "undefined references.",
                                    "rerun "
                                    )
        self.__serie = _serie
        self.__exercise = _exercise
        self.__exclude_from_zip = set(['nbproject'])

    def createNewExercice(self):
        self.__exercise = Utils.nextUnusedExercice(self.__exoDirName)
        self.__log.debug("Creating Exercice Structure %s", self.__exercise)
        os.chdir(self.__cwd)
        os.mkdir(self.__exoDirName+"/"+"ex"+str(self.__exercise))
        for adir in self.__exoStructure:
            os.mkdir(self.__exoDirName+"/"+"ex"+str(self.__exercise)+"/"+adir)
        extex = open(self.__exoDirName+"/"+"ex"+str(self.__exercise)+"/latex/exo.tex", 'w')
        soltex = open(self.__exoDirName+"/"+"ex"+str(self.__exercise)+"/latex/exosol.tex", 'w')
        extex.write("\exercice{}\n")
        extex.write("voir le site \cite{WEBT} et \cite{T03}")
        soltex.write("\exercice{}\n")
        soltex.write("voir le site \cite{WEBT} et \cite{T03}")
        extex.close()
        soltex.close()

    def buildSerie(self):
        if self.__smscupdateBibTex:
            Utils.doUpdateBibTex(self.__smscbibtex, self.__noCiteList)
        seriesConfig = ConfigParser.SafeConfigParser()
        self.__log.debug(self.__seriesConfigDir+"/serie"+str(self.__serie)+".cfg")
        seriesConfig.read(self.__seriesConfigDir+"/serie"+str(self.__serie)+".cfg")
        titles = seriesConfig.get('Serie', 'titles')
        numbers = seriesConfig.get('Serie', 'exo-numbers')
        #draft = seriesConfig.getboolean('Serie', 'draft')
        # check if dir exists with os.path.isdir
        if os.path.isdir(os.path.join(self.__outputDir, self.__smscmoodleOutputDir+str(self.__serie))):
            shutil.rmtree(os.path.join(self.__outputDir, self.__smscmoodleOutputDir+str(self.__serie)))
        os.mkdir(os.path.join(self.__outputDir, self.__smscmoodleOutputDir+str(self.__serie)))
        os.mkdir(os.path.join(os.path.join(self.__outputDir, self.__smscmoodleOutputDir+str(self.__serie)),'donne'))
        os.mkdir(os.path.join(os.path.join(self.__outputDir, self.__smscmoodleOutputDir+str(self.__serie)),'solution'))

        outputDir=os.path.join(os.path.join(self.__outputDir, self.__smscmoodleOutputDir+str(self.__serie)),'donne')
        self.__doCreateSerie(titles.split(','), numbers.split(','), outputDir)
        outputDir =  os.path.join(os.path.join(self.__outputDir, self.__smscmoodleOutputDir+str(self.__serie)),'solution')
        self.__doCreateSolution(titles.split(','), numbers.split(','), outputDir)
        self.__addCodeDonne(numbers.split(","))
        self.__addCodeSolution(numbers.split(","))

        Utils.cleanTempFiles(self.__keepTempFiles)

    def __doCreateSerie(self, _titles, _numbers, _outputDir, filename = None):
        filename = filename or "serie"+str(self.__serie)
        texfile = os.path.join("/tmp/", filename+".tex")
        serie = open(texfile, 'w') #use open(file 'a') for appending to a given file
        self.__smscsolutiontext = ''
        latex = LaTeX(self.__serie)
        latex.createHeader(serie, _titles)

        for number in _numbers:
            serie.write(r'\setcounter{section}{'+number+'}\n')
            serie.write(r'\addtocounter{section}{-1}'+'\n')
            serie.write(r'\renewcommand{\includepath}{\compilationpath/'+self.__exoDirName+'/ex'+number+'/latex/ressources}'+'\n')
            exo = open(self.__exoDirName+"/"+"ex"+number+"/latex/exo.tex", 'r')
            for line in exo:
                serie.write(line)

        latex.createFooter(serie)
        serie.close()

        Utils.doLatex(texfile, _outputDir)
        return os.path.join(_outputDir, filename+".pdf")


    def __doCreateSolution(self, _titles, _numbers, _outputDir, filename = None):
        filename = filename or "solution"+str(self.__serie)
        texfile = os.path.join("/tmp/", filename+".tex")
        solution = open(texfile, 'w')
        latex = LaTeX(self.__serie)
        latex.createHeader(solution, _titles, True)

        for number in _numbers:
            solution.write(r'\setcounter{section}{'+number+'}\n')
            solution.write(r'\addtocounter{section}{-1}'+'\n')
            solution.write(r'\renewcommand{\includepath}{\compilationpath/'+self.__exoDirName+'/ex'+number+'/latex/ressources}'+'\n')
            exo = open(self.__exoDirName+"/"+"ex"+number+"/latex/exosol.tex", 'r')
            for line in exo:
                solution.write(line)

        latex.createFooter(solution)
        solution.close()

        Utils.doLatex(texfile, _outputDir)
        return os.path.join(_outputDir, filename+".pdf")

    def __addCodeDonne(self, _exonumbers):
        """Add the code skeletons which are given wich each exercise"""
        self.__log.info("Adding source code for donnee")
        for number in _exonumbers:
            #ZipUtils.myZip(self.__exoDirName+"/"+"ex"+number+"/code/donne", os.path.join(os.path.join(self.__outputDir,self.__smscmoodleOutputDir+str(self.__serie)),'donne/donnee_s'+str(self.__serie)+'_e'+number+'.zip'), 'donnee_s'+str(self.__serie)+'_e'+number)
            ZipUtils.myTar(self.__exoDirName+"/"+"ex"+number+"/code/donne", os.path.join(os.path.join(self.__outputDir,self.__smscmoodleOutputDir+str(self.__serie)),'donne/donnee_s'+str(self.__serie)+'_e'+number+'.tar.gz'), 'donnee_s'+str(self.__serie)+'_e'+number)
            #ZipUtils.sysTar(self.__exoDirName+"/"+"ex"+number+"/code/donne", os.path.join(os.path.join(self.__outputDir,self.__smscmoodleOutputDir+str(self.__serie)),'donne/donnee_s'+str(self.__serie)+'_e'+number+'.tar.gz'), 'donnee_s'+str(self.__serie)+'_e'+number)

    def __addCodeSolution(self, _exonumbers):
        """Adds code solutions, if any"""
        self.__log.info("Adding source code for solution")
        for number in _exonumbers:
            #ZipUtils.myZip(self.__exoDirName+"/"+"ex"+number+"/code/solution", os.path.join(os.path.join(self.__outputDir, self.__smscmoodleOutputDir+str(self.__serie)), 'solution/solution_s'+str(self.__serie)+'_e'+number+'.zip'), 'solution_s'+str(self.__serie)+'_e'+number)
            ZipUtils.myTar(self.__exoDirName+"/"+"ex"+number+"/code/solution", os.path.join(os.path.join(self.__outputDir, self.__smscmoodleOutputDir+str(self.__serie)), 'solution/solution_s'+str(self.__serie)+'_e'+number+'.tar.gz'), 'solution_s'+str(self.__serie)+'_e'+number)
            #ZipUtils.sysTar(self.__exoDirName+"/"+"ex"+number+"/code/solution", os.path.join(os.path.join(self.__outputDir, self.__smscmoodleOutputDir+str(self.__serie)), 'solution/solution_s'+str(self.__serie)+'_e'+number+'.tar.gz'), 'solution_s'+str(self.__serie)+'_e'+number)

    def buildAllSeries(self):
        """Builds all configured Series"""
        seriesConfigFiles = os.listdir(self.__seriesConfigDir)
        seriesConfigFiles = Utils.natsort(seriesConfigFiles)
        #seriesConfigFiles.sort()
        if os.path.isdir(self.__smscmoodleOutputDir):
            shutil.rmtree(self.__smscmoodleOutputDir)
        os.mkdir(self.__smscmoodleOutputDir)
        self.__outputDir = self.__smscmoodleOutputDir
        for config in seriesConfigFiles:
            if not config.startswith("."):
                self.__log.debug("Will treat from file: "+config+" serie:"+config.split(".")[0].partition("serie")[2])
                self.__serie=config.split(".")[0].partition("serie")[2]
                self.__log.info("Found Serie "+self.__serie+". Will now build it.")
                self.buildSerie()


    def makeWorkbook(self):
        seriesConfigFiles = os.listdir(self.__seriesConfigDir)
        #seriesConfigFiles.sort()
        seriesConfigFiles = Utils.natsort(seriesConfigFiles)
        if os.path.isdir(self.__smscmoodleOutputDir):
            shutil.rmtree(self.__smscmoodleOutputDir)
        os.mkdir(self.__smscmoodleOutputDir)
        self.__outputDir = self.__smscmoodleOutputDir
        for config in seriesConfigFiles:
            self.__serie=int(config.split(".")[0].partition("serie")[2])
            self.__log.info("Found Serie "+str(self.__serie)+". Will now build it.")
            seriesConfig = ConfigParser.SafeConfigParser()
            self.__log.debug("Reading "+self.__seriesConfigDir+"/serie"+str(self.__serie)+".cfg")
            seriesConfig.read(self.__seriesConfigDir+"/"+config)
            titles = seriesConfig.get('Serie', 'titles')
            numbers = seriesConfig.get('Serie', 'exo-numbers')

            outputDir = self.__smscmoodleOutputDir
            seriesname = str(self.__serie)+"serie"
            seriesname = self.__doCreateSerie(titles.split(','), numbers.split(','), outputDir, seriesname)
            solutionname = str(self.__serie)+"solution"
            solutionname = self.__doCreateSolution(titles.split(','), numbers.split(','), outputDir, solutionname)

        self.__makeWorkBookTitlePage(outputDir)
        if self.__usepdftk:
            subprocess.call(["pdftk "+outputDir+"/*.pdf cat output workbook.pdf"], shell=True, cwd="./", stdout=DEVNULL, stderr=STDOUT)
        else:
            subprocess.call(["gs -q -dNOPAUSE -dBATCH -sDEVICE=pdfwrite -sOutputFile=workbook.pdf "+outputDir+"/*.pdf"], shell=True, cwd="./", stdout=DEVNULL, stderr=STDOUT)
        shutil.rmtree(self.__smscmoodleOutputDir)
        Utils.cleanTempFiles(self.__keepTempFiles)


    def __makeWorkBookTitlePage(self, _outputDir):
        texfile = "/tmp/0wbtitlepage.tex"
        wbtitle = open(texfile, 'w')
        latex = LaTeX(self.__serie)
        latex.makeWorkBookTitlePageHeader(wbtitle)
        seriesConfigFiles = os.listdir(self.__seriesConfigDir)
        #seriesConfigFiles.sort()
        seriesConfigFiles = Utils.natsort(seriesConfigFiles)
        for config in seriesConfigFiles:
            seriesConfig = ConfigParser.SafeConfigParser()
            seriesConfig.read(self.__seriesConfigDir+"/"+config)
            titles = seriesConfig.get('Serie', 'titles')
            numbers = seriesConfig.get('Serie', 'exo-numbers')
            serienumber = config.split(".")[0].partition("serie")[2]
            wbtitle.write(r"\textsf{ \textbf{S{\'e}rie "+serienumber+"}} \dotfill"+"\n")
            for number in numbers.split(","):
                wbtitle.write(number+"\n")
            wbtitle.write(r"\begin{itemize}"+"\n")
            for title in titles.split(","):
                wbtitle.write(r"\item "+title+"\n")
            wbtitle.write(r"\end{itemize}"+"\n")
        latex.printWorkBookTitlePageFooter(wbtitle)
        wbtitle.close()
        Utils.doLatex(texfile, _outputDir, True)

    def makeCatalogue(self):
        """Creates a pdf containing all exercises. Each exercise is always followed by its solution"""
        afile = "/tmp/catalogue.tex"
        self.__serie=0
        if os.path.isdir("Catalogue"):
            shutil.rmtree("Catalogue")
        os.mkdir("Catalogue")
        catalogue = open(afile, 'w') #use open(file 'a') for appending to a given file
        latex = LaTeX(self.__serie)
        latex.createHeader(catalogue, [])
        catalogue.write(r'\renewcommand{\exercice}[1]{\subsection*{Problem: #1}}'+"\n")
        catalogue.write(r'\renewcommand{\solution}[1]{\subsection*{Solution: #1}}'+"\n")
        catalogue.write(r'\renewcommand{\question}[1]{\subsubsection*{#1}}'+"\n")
        catalogue.write(r''+"\n")
        catalogue.write(r'\makeatletter'+"\n")
        catalogue.write(r'\renewcommand{\section}{\@startsection{section}{3}{2pt}{12pt}{10pt}{\center \huge \sffamily \bfseries}}'+"\n")
        catalogue.write(r'\renewcommand{\thesection}{(\roman{section})}'+"\n")
        catalogue.write(r'\renewcommand{\thesubsection}{(\roman{subsection})}'+"\n")
        exos = os.listdir(self.__exoDirName)
        #exos.sort()
        exos = Utils.natsort(exos)
        for exo in exos:
            if exo.find("ex") != -1:
                number = exo[2:]
                catalogue.write(r'\section*{Exercise '+number+'}'+"\n")
                catalogue.write(r'\renewcommand{\includepath}{\compilationpath/'+self.__exoDirName+'/ex'+number+'/latex/resources}'+'\n')
                exo = open(os.path.join(os.path.join(self.__exoDirName, "ex"+number),"latex/exo.tex"), 'r')
                for line in exo:
                    catalogue.write(line)
                exo.close()
                catalogue.write(r'\renewcommand{\includepath}{\compilationpath/'+self.__exoDirName+'/ex'+number+'/latex/resources}'+'\n')
                solution = open(os.path.join(os.path.join(self.__exoDirName, "ex"+number),"latex/exosol.tex"), 'r')
                for line in solution:
                    catalogue.write(line)
                solution.close()
                if self.__smscaddClearPage:
                    catalogue.write("\clearpage")


        latex.createFooter(catalogue)
        catalogue.close()
        outputDir = "Catalogue"
        Utils.doLatex(afile, outputDir, True)
        basename = os.path.split(afile)[1].split(".")[0]
        shutil.move(os.path.join(outputDir, basename+".pdf"), basename+".pdf")
        shutil.rmtree(outputDir)

    def previewExercice(self):
        self.__serie = 0
        self. __doCreateSerie([], [str(self.__exercise)], "/tmp/")
        if self.__smscopencmd.find(",") == -1:
            cmd = self.__smscopencmd
            arg = [cmd, "/tmp/serie0.pdf"]
        else:
            cmd = self.__smscopencmd.split(",")[0]
            arg = self.__smscopencmd.split(",")[1:]
            arg.append("/tmp/serie0.pdf")
            arg.insert(0, cmd)
        subprocess.Popen(cmd+" /tmp/serie0.pdf", shell=True)

    def previewSolution(self):
        self.__serie = 0
        self. __doCreateSolution([], [str(self.__exercise)], "/tmp/")
        if self.__smscopencmd.find(",") == -1:
            cmd = self.__smscopencmd
            arg = [cmd, "/tmp/solution0.pdf"]
        else:
            cmd = self.__smscopencmd.split(",")[0]
            arg = self.__smscopencmd.split(",")[1:]
            arg.append("/tmp/solution0.pdf")
            arg.insert(0, cmd)
        subprocess.Popen(cmd+" /tmp/solution0.pdf", shell=True)


    def createNewLecture(self, lecturename):
        """Create the directory structure for a new lecture"""
        if os.path.exists(lecturename):
            self.__log.critical("This lecture already exists. Please choose another name")
            return -1
        os.mkdir(lecturename)
        os.mkdir(join(lecturename, 'Exercises'))
        os.mkdir(join(lecturename, 'Series_properties'))
        f = open(join(join(lecturename, 'Series_properties'), 'serie1.cfg'),'w')
        f.write('[Serie]\n')
        f.write('titles: Classes et ADT, Programmation orient\'ee objets en Java - types statique et dynamique, Java: h\'eritage - polymorphisme - interfaces - ...\n')
        f.write('exo-numbers: 3,1,2\n')
        f.close()
        self.__log.debug(resource_filename(__name__, 'data'))
        copy_tree(resource_filename(__name__, 'data'),
                        lecturename)

    def doZip(self):
        if self.__smscdozipfiles:
            self.__log.info("Zipping " + self.__smscmoodleOutputDir + " into " + self.__smscmoodleOutputDir + '.zip')
            ZipUtils.myZip(self.__smscmoodleOutputDir, self.__smscmoodleOutputDir + '.zip', self.__smscmoodleOutputDir)
            if self.__smscremoveUnzipped:
                shutil.rmtree(self.__smscmoodleOutputDir)

        
class checkInstallException(Exception):
    """Used for raising exception during doCheckInstall of SMS class"""
    def __init__(self, missingProg):
        message = ""
        for prog in missingProg:
            message += prog
            message += "; "
        message = message[0:len(message)-2]
        self.missing = message


