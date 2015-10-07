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
from subprocess import STDOUT
try:
    from subprocess import DEVNULL # py3k
except ImportError:
    import os
    DEVNULL = open(os.devnull, 'wb')
from pkg_resources import resource_filename
from distutils.dir_util import copy_tree
from os.path import dirname, join, expanduser
from utils import Utils, ZipUtils
from utils.LaTeX import *

class SMS:
    def __init__(self):

        self.__INSTALL_DIR = dirname(__file__)
        self.__CONFIG_DIR = '/etc/SeriesManagementSystem/'
        logging.basicConfig(level=logging.ERROR)
        logging.config.fileConfig(
            [join(self.__CONFIG_DIR, 'logging.conf'), expanduser('~/.logging.conf'), 'logging.conf'])
        self.__log = logging.getLogger('seriesManagementSystem')
        
        self.__cwd = os.getcwd()
        self.__keepTempFiles = False
        
        self.__log.debug("\033[1;33m"+self.__cwd+"\033[0m")
        self.__exoStructure = ["code", "code/donne", "code/solution", "latex", "latex/ressources", "latex/ressources/figures", "latex/ressources/code"]

        smsConfig = ConfigParser.SafeConfigParser()
        self.__log.debug("Reading general configuration from lecture.cfg")
        smsConfig.read([join(resource_filename(__name__, 'data'), 'lecture.cfg'), "lecture.cfg"])
        self.__smscmoodleOutputDir = smsConfig.get("Config", "moodleOutputDir")
        self.__smscremoveUnzipped = smsConfig.getboolean("Config", "removeUnzipped")
        self.__smscdozipfiles = smsConfig.getboolean("Config",  "createZip")
        self.__smscupdateBibTex = smsConfig.getboolean("Config", "updateBibTex")
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
        self.__serie = -1
        self.__exercise = -1
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

        Utils.cleanTempFiles([])

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
        Utils.cleanTempFiles([])


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

    def usage(self):
        print ('Usage:')
        print (os.path.basename(sys.argv[0])+' <command> [option]') #sys.argv[0]
        print ('\033[1;33mWhere option is one of:\033[0m')
        print ('    -e for specifying an exercise')
        print ('    -s for specifying a serie')
        print ('    -u for updating last visited date in bibtex')
        print ('    -k for keeping unzipped files')
        print ('    -t for keeping temporary files in /tmp')
        print ('    -z for doing a zip file')
        print ('    -l lecture name')
        print ('\033[1;33mWhere command is one of:\033[0m')
        print ('    --make-new-exercise.........................Creates a new exercise structure')
        print ('    --build-serie (-s option mandatory).........Builds all for the specified serie')
        print ('    --build-all-series..........................Builds all available series with their solutions')
        print ('    --make-workbook.............................Creates one big PDF containig all concatenated series')
        print ('    --make-catalogue............................Creates a PDF containing all exercices and their solutions')
        print ('    --preview-exercise (-e option mandatory)....Previews the specified exercise')
        print ('    --preview-solution (-e option mandatory)....Previews the solution for the specified exercise')
        print ('    --make-new-lecture (-l option mandatory)....Creates the directory structure for a new Lecture')


    def getArguments(self, argv):
        # Parse the command line options
        if len(argv) == 0:
            self.usage()
            sys.exit(3)
        try:
            options, args = getopt.getopt(argv, "e:s:huktzl:", ["make-new-lecture", "make-new-exercise", "build-serie", "build-all-series", "make-workbook", "make-catalogue", "preview-exercise", "preview-solution", "--help"])
        except getopt.GetoptError:
            self.usage()
            sys.exit(2)
        Utils.cleanDSStore("./")
        Utils.doCheckInstall()
        self.__log.debug("Parsing options")
        for option, arg in options:
            self.__log.debug("Passed options are  %s  and args are %s", option, arg)

            if option in ["-e"]:
                self.__log.info("Current exercise is: %s", arg)
                self.__exercise=int(arg)
            elif option in ["-s"]:
                self.__log.info("Current serie is: %s", arg)
                self.__serie=int(arg)
            if option in ["-u"]:
                if self.__smscupdateBibTex:
                    self.__smscupdateBibTex=False
                else:
                    self.__log.info("Updating Bibtex Last visited date")
                    self.__smscupdateBibTex=True
            if option in ["-k"]:
                if self.__smscremoveUnzipped:
                    self.__smscremoveUnzipped = False
                else:
                    self.__log.info("Keeping unzipped files")
                    self.__smscremoveUnzipped = True
            if option in ["-t"]:
                self.__keepTempFiles = True
            if option in ["-z"]:
                self.__log.info("Will zip the files")
                self.__smscdozipfiles = True
            if option in ["-l"]:
                lecturename = arg
        self.__log.debug("Parsing arguments")
        for option, arg in options:
            self.__log.debug("Passed options are  \"%s\"  and args are \"%s\"", option, arg)
            if option in ["--make-new-exercise"]:
                self.__log.info("Creating a new Exercice")
                self.createNewExercice()
                break
            elif option in ["--build-serie"]:
                if self.__serie == -1:
                    self.__serie = int(raw_input ("Which serie do you want to build? "))
                self.__log.info("Building Serie %s", self.__serie)
                self.buildSerie()
                if self.__smscdozipfiles:
                    self.__log.info("Zipping "+self.__smscmoodleOutputDir+str(self.__serie)+" into "+self.__smscmoodleOutputDir+str(self.__serie)+'.zip')
                    ZipUtils.myZip(self.__smscmoodleOutputDir+str(self.__serie), self.__smscmoodleOutputDir+str(self.__serie)+'.zip', self.__smscmoodleOutputDir+str(self.__serie))
                    if self.__smscremoveUnzipped:
                        shutil.rmtree(self.__smscmoodleOutputDir+str(self.__serie))
                    break
            elif option in ["--build-all-series"]:
                self.__log.info("Building All Available Series")
                self.buildAllSeries()
                if self.__smscdozipfiles:
                    self.__log.info("Zipping "+self.__smscmoodleOutputDir+" into "+self.__smscmoodleOutputDir+'.zip')
                    ZipUtils.myZip(self.__smscmoodleOutputDir, self.__smscmoodleOutputDir+'.zip', self.__smscmoodleOutputDir)
                    if self.__smscremoveUnzipped:
                        shutil.rmtree(self.__smscmoodleOutputDir)
                    break
            elif option in ["--make-workbook"]:
                self.__log.info("Building Workbook")
                self.makeWorkbook()
                break
            elif option in ["--make-catalogue"]:
                self.__log.info("Creating Catalogue of available Exercices")
                self.makeCatalogue()
                break
            elif option in ["--preview-exercise"]:
                if self.__exercise == -1:
                    self.__exercise = int(raw_input ("Which exercise do you want to preview? "))
                self.__log.info("Previewing exercise %s", self.__exercise)
                self.previewExercice()
                break
            elif option in ["--preview-solution"]:
                if self.__exercise == -1:
                    self.__exercise = int(raw_input ("Which solution do you want to preview? "))
                self.__log.info("Previewing solution %s", self.__exercise)
                self.previewSolution()
                break
            elif option in ["--make-new-lecture"]:
                self.createNewLecture(lecturename)
            elif option in ["--help", "-h"]:
                self.usage()
                break
        
class checkInstallException(Exception):
    """Used for raising exception during doCheckInstall of SMS class"""
    def __init__(self, missingProg):
        message = ""
        for prog in missingProg:
            message += prog
            message += "; "
        message = message[0:len(message)-2]
        self.missing = message

if __name__ == "__main__":
    sms = SMS()
    sms.getArguments(sys.argv[1:])
