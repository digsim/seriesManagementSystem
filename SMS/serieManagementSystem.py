#!/usr/bin/python
# -*- coding: utf-8 -*-

##############################################################################################################
# This script is a simple management system for series made of exercises and solution.                                                                                                                                                    #
# It is possible to make zipped series for moodle, a zip containing all series. Furthermore one can                                                                                                                                   #
# generate previews for one exercise/solution. Two handy functions are the make-workbook and the                                                                                                                               #
# make-catalogue. The former one creaets a pdf containig all series, each one followed by its solution                                                                                                                             #
# just like they were distributed. The latter one create a sort of index of all available exercises in                                                                                                                                    #
# the system. Each exercise is followed by its solution.                                                                                                                                                                                                        #
#                                                                                                                                                                                                                                                                                             #
# The structure for a new exercise should be created by using the make-new-exercise function.                                                                                                                                       #
# For further help, please refer to the help function of the software.                                                                                                                                                                                   #
# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
#                                                                                                                                                                                                                                                                                             #
# Author: Andreas Ruppen                                                                                                                                                                                                                                                    #
# License: GPL                                                                                                                                                                                                                                                                       #
# This program is free software; you can redistribute it and/or modify                                                                                                                                                                                 #
#   it under the terms of the GNU General Public License as published by                                                                                                                                                                            #
#   the Free Software Foundation; either version 2 of the License, or                                                                                                                                                                                    #
#   (at your option) any later version.                                                                                                                                                                                                                                      #
#                                                                                                                                                                                                                                                                                               #
#   This program is distributed in the hope that it will be useful,                                                                                                                                                                                            #
#   but WITHOUT ANY WARRANTY; without even the implied warranty of                                                                                                                                                                            #
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the                                                                                                                                                                     #
#   GNU General Public License for more details.                                                                                                                                                                                                                   #
#                                                                                                                                                                                                                                                                                                #
#   You should have received a copy of the GNU General Public License                                                                                                                                                                                 #
#   along with this program; if not, write to the                                                                                                                                                                                                                         #
#   Free Software Foundation, Inc.,                                                                                                                                                                                                                                           #
#   59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.                                                                                                                                                                                              #
################################################################################################################
import sys, os, getopt, shutil
import logging
import logging.config
if float(sys.version[:3])<3.0:
    import ConfigParser
else: 
    import configparser as ConfigParser
import subprocess
import zipfile
import tarfile
import datetime
import re
from os.path import dirname, join, expanduser

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
        smsConfig.read([join(self.__CONFIG_DIR, 'lecture.cfg'), expanduser('~/.lecture.cfg'), 'lecture.cfg'])
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

    def doCreateNewExercice(self):
        self.__exercise = self.__nextUnusedExercice()
        self.__log.debug("Creating Exercice Structure %s", self.__exercise)
        os.chdir(self.__cwd)
        os.mkdir(self.__exoDirName+"/"+"ex"+str(self.__exercise))
        for adir in self.__exoStructure:
            os.mkdir(self.__exoDirName+"/"+"ex"+str(self.__exercise)+"/"+adir)
        extex = open(self.__exoDirName+"/"+"ex"+str(self.__exercise)+"/latex/exo"+str(self.__exercise)+".tex", 'w')
        soltex = open(self.__exoDirName+"/"+"ex"+str(self.__exercise)+"/latex/exo"+str(self.__exercise)+"sol.tex", 'w')
        extex.write("\exercice{}\n")
        extex.write("voir le site \cite{WEBT} et \cite{T03}")
        soltex.write("\exercice{}\n")
        soltex.write("voir le site \cite{WEBT} et \cite{T03}")
        extex.close()
        soltex.close()

    def __nextUnusedExercice(self):
        lastExo = 0
        dirs = os.listdir(self.__exoDirName)
        dirs = self.natsort(dirs)
        for adir in dirs:
            exoNumber = int(adir.partition('ex')[2])
            if exoNumber > lastExo:
                lastExo = exoNumber
        lastExo =  int(lastExo)+1
        return lastExo

    def __doBuildSerie(self):
        if self.__smscupdateBibTex:
            self.__doUpdateBibTex()
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

        self.__cleanTempFiles()

    def buildSerie(self, seriesnumber):
        self.__serie = seriesnumber
        self.__doBuildSerie()

    def __doCreateSerie(self, _titles, _numbers, _outputDir):
        afile = "/tmp/serie"+str(self.__serie)+".tex"
        serie = open(afile, 'w') #use open(file 'a') for appending to a given file
        self.__smscsolutiontext = ''
        self.__createHeader(serie, _titles)


        for number in _numbers:
            serie.write(r'\setcounter{section}{'+number+'}\n')
            serie.write(r'\addtocounter{section}{-1}'+'\n')
            serie.write(r'\renewcommand{\includepath}{\compilationpath/'+self.__exoDirName+'/ex'+number+'/latex/resources}'+'\n')
            exo = open(self.__exoDirName+"/"+"ex"+number+"/latex/exo"+number+".tex", 'r')
            for line in exo:
                serie.write(line)

        self.__createFooter(serie)
        serie.close()

        self.__doLatex(afile, _outputDir)


    def __doCreateSolution(self, _titles, _numbers, _outputDir):
        afile = "/tmp/solution"+str(self.__serie)+".tex"
        solution = open(afile, 'w')
        self.__smscsolutiontext = 'Solution'
        self.__createHeader(solution, _titles)

        for number in _numbers:
            solution.write(r'\setcounter{section}{'+number+'}\n')
            solution.write(r'\addtocounter{section}{-1}'+'\n')
            solution.write(r'\renewcommand{\includepath}{\compilationpath/'+self.__exoDirName+'/ex'+number+'/latex/resources}'+'\n')
            exo = open(self.__exoDirName+"/"+"ex"+number+"/latex/exo"+number+"sol.tex", 'r')
            for line in exo:
                solution.write(line)

        self.__createFooter(solution)
        solution.close()

        self.__doLatex(afile, _outputDir)

    def __createHeader(self, _file, _titles):
        _file.write(r'\documentclass[francais,a4paper]{article}'+"\n")
        _file.write(r'\usepackage{sms}'+"\n")
        _file.write(r"\newcommand{\compilationpath}{./}"+"\n")
        _file.write(r'\newcommand{\prof}{'+self.__smsclecturer+'}'+"\n")
        _file.write(r'\newcommand{\course}{'+self.__smscname+'}'+"\n")
        _file.write(r'\newcommand{\theyear}{'+self.__smscyear+'}'+"\n")
        _file.write(r'\newcommand{\exercisetext}{'+self.__smscexercisetext+'}'+"\n")
        _file.write(r'\newcommand{\solutiontext}{'+self.__smscsolutiontext+'}'+"\n")
        _file.write(r'\newcommand{\thecontent} {\sffamily\bfseries '+self.__smsccontenttext+':}'+"\n")
        _file.write(r'\newcommand{\theheadertitle}{'+self.__smscheadertitle+'}'+"\n")
        _file.write(r'\newcommand{\unilogo}{'+self.__smscunilogo+'}'+"\n")
        _file.write(r'\newcommand{\groupelogo}{'+self.__smscgroupelogo+'}'+"\n")
        #afile.write(r"\input{\compilationpath/exercicepreamble}"+"\n")
        _file.write(r"% Number of the serie"+"\n")
        _file.write(r"\newcommand{\exercisenb}{"+str(self.__serie)+"}"+"\n")
        _file.write(r"\newcommand{\includepath}{\compilationpath}"+"\n")
        _file.write(r'\hypersetup{pdftitle={'+self.__smscpdftitle+'},pdfauthor={'+self.__smscpdfauthor+'},pdfkeywords={'+self.__smscpdfkeyword+"}}\n")
        _file.write(r"\begin{document}"+"\n")
        _file.write(r"\input{\compilationpath/captionnames}"+"\n")
        _file.write(r"% Header of the exercise:"+"\n")
        _file.write(r"\exheader"+"\n")

        if len(_titles) != 0:
            _file.write(r"% Content of the exercise, topics"+"\n")
            _file.write(r"\content{"+"\n")
            _file.write(r"\begin{itemize}"+"\n")
            for title in _titles:
                _file.write(r'\item '+title+'\n')
            _file.write(r'\end{itemize}'+'\n')
            _file.write(r'}'+'\n')

    def __createFooter(self, _file):
        for bib in self.__noCiteList:
            _file.write(r'\nocite{'+bib+'}\n')
        _file.write(r'\bibliography{bibdb}'+'\n')
        _file.write(r'\bibliographystyle{plain}'+'\n')
        _file.write(r'\end{document}'+'\n')

    def __addCodeDonne(self, _exonumbers):
        """does nothing"""
        self.__log.info("Adding source code for donnee")
        for number in _exonumbers:
            #self.__myZip(self.__exoDirName+"/"+"ex"+number+"/code/donne", os.path.join(os.path.join(self.__outputDir,self.__smscmoodleOutputDir+str(self.__serie)),'donne/donnee_s'+str(self.__serie)+'_e'+number+'.zip'), 'donnee_s'+str(self.__serie)+'_e'+number)
            self.__myTar(self.__exoDirName+"/"+"ex"+number+"/code/donne", os.path.join(os.path.join(self.__outputDir,self.__smscmoodleOutputDir+str(self.__serie)),'donne/donnee_s'+str(self.__serie)+'_e'+number+'.tar.gz'), 'donnee_s'+str(self.__serie)+'_e'+number)
            #self.__sysTar(self.__exoDirName+"/"+"ex"+number+"/code/donne", os.path.join(os.path.join(self.__outputDir,self.__smscmoodleOutputDir+str(self.__serie)),'donne/donnee_s'+str(self.__serie)+'_e'+number+'.tar.gz'), 'donnee_s'+str(self.__serie)+'_e'+number)

    def __addCodeSolution(self, _exonumbers):
        """does nothing"""
        self.__log.info("Adding source code for solution")
        for number in _exonumbers:
            #self.__myZip(self.__exoDirName+"/"+"ex"+number+"/code/solution", os.path.join(os.path.join(self.__outputDir, self.__smscmoodleOutputDir+str(self.__serie)), 'solution/solution_s'+str(self.__serie)+'_e'+number+'.zip'), 'solution_s'+str(self.__serie)+'_e'+number)
            self.__myTar(self.__exoDirName+"/"+"ex"+number+"/code/solution", os.path.join(os.path.join(self.__outputDir, self.__smscmoodleOutputDir+str(self.__serie)), 'solution/solution_s'+str(self.__serie)+'_e'+number+'.tar.gz'), 'solution_s'+str(self.__serie)+'_e'+number)
            #self.__sysTar(self.__exoDirName+"/"+"ex"+number+"/code/solution", os.path.join(os.path.join(self.__outputDir, self.__smscmoodleOutputDir+str(self.__serie)), 'solution/solution_s'+str(self.__serie)+'_e'+number+'.tar.gz'), 'solution_s'+str(self.__serie)+'_e'+number)

    def doBuildAllSeries(self):
        seriesConfigFiles = os.listdir(self.__seriesConfigDir)
        #seriesConfigFiles.sort()
        seriesConfigFiles = self.natsort(seriesConfigFiles)
        if os.path.isdir(self.__smscmoodleOutputDir):
            shutil.rmtree(self.__smscmoodleOutputDir)
        os.mkdir(self.__smscmoodleOutputDir)
        self.__outputDir = self.__smscmoodleOutputDir
        for config in seriesConfigFiles:
            if not config.startswith("."):
                self.__log.debug("Will treat from file: "+config+" serie:"+config.split(".")[0].partition("serie")[2])
                #self.__serie=int(config.split(".")[0].partition("serie")[2])
                #self.__log.info("Found Serie "+str(self.__serie)+". Will now build it.")
                self.__serie=config.split(".")[0].partition("serie")[2]
                self.__log.info("Found Serie "+self.__serie+". Will now build it.")
                self.__doBuildSerie()


    def doMakeWorkbook(self):
        seriesConfigFiles = os.listdir(self.__seriesConfigDir)
        #seriesConfigFiles.sort()
        seriesConfigFiles = self.natsort(seriesConfigFiles)
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
            outputDir=self.__smscmoodleOutputDir
            self.__doCreateSerie(titles.split(','), numbers.split(','), outputDir)
            outputDir =  self.__smscmoodleOutputDir
            self.__doCreateSolution(titles.split(','), numbers.split(','), outputDir)
        self.__makeWorkBookTitlePage(outputDir)
        if self.__usepdftk:
            subprocess.call(["pdftk "+outputDir+"/*.pdf cat output workbook.pdf"], shell=True, cwd="./", stdout=open("/dev/stdout", 'w'))
        else:
            subprocess.call(["gs -q -dNOPAUSE -dBATCH -sDEVICE=pdfwrite -sOutputFile=workbook.pdf "+outputDir+"/*.pdf"], shell=True, cwd="./", stdout=open("/dev/stdout", 'w'))
        shutil.rmtree(self.__smscmoodleOutputDir)
        self.__cleanTempFiles()


    def __makeWorkBookTitlePage(self, _outputDir):
        file = "/tmp/0wbtitlepage.tex"
        self.__makeWorkBookTitlePageHeader(file)
        wbtitle = open(file, 'a')
        seriesConfigFiles = os.listdir(self.__seriesConfigDir)
        #seriesConfigFiles.sort()
        seriesConfigFiles = self.natsort(seriesConfigFiles)
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
        wbtitle.close()
        self.__printWorkBookTitlePageFooter(file)
        self.__doLatex(file, _outputDir, False)

    def __makeWorkBookTitlePageHeader(self, _file):
        wbtitle = open(_file, 'w')
        wbtitle.write(r"\documentclass[francais,a4paper]{article}"+"\n")
        wbtitle.write(r"\newcommand{\compilationpath}{./}"+"\n")
        wbtitle.write(r'\newcommand{\groupelogo}{'+self.__smscgroupelogo+'}'+"\n")
        wbtitle.write(r"\usepackage{graphicx}"+"\n")
        wbtitle.write(r"\usepackage{palatino}"+"\n")
        wbtitle.write(r"%\usepackage[french]{babel}"+"\n")
        wbtitle.write(r"\usepackage[utf8]{inputenc}"+"\n")
        wbtitle.write(r"\usepackage{ae, pslatex}    % Joli output en PDF"+"\n")
        wbtitle.write(r"%\usepackage{graphics}          % Manipulation de boîtes et importation de graphismes."+"\n")
        wbtitle.write(r"%\usepackage[dvips]{graphicx}   %"+"\n")
        wbtitle.write(r"\usepackage[T1]{fontenc}"+"\n")
        wbtitle.write(r"\begin{document}"+"\n")
        wbtitle.write(r"\pagestyle{empty}"+"\n")
        wbtitle.write(r"\vspace{-1cm}"+"\n")
        wbtitle.write(r"\begin{center}"+"\n")
        wbtitle.write(r"\begin{Huge}"+"\n")
        wbtitle.write(r"{\sf "+self.__smscname+" }"+"\n")
        wbtitle.write(r"\end{Huge}"+"\n")
        wbtitle.write(r"\vspace{0.4cm}%"+"\n")
        wbtitle.write(r"\begin{huge}"+"\n")
        wbtitle.write(r"Workbook ("+self.__smscyear+")"+"\n")
        wbtitle.write(r"\end{huge}"+"\n")
        wbtitle.write(r"\end{center}"+"\n")
        wbtitle.write(r"\rule{\linewidth}{1pt}"+"\n")
        wbtitle.write(r"\vspace{1cm}"+"\n")
        wbtitle.close()

    def __printWorkBookTitlePageFooter(self, _file):
        wbtitle = open(_file, 'a')
        wbtitle.write(r"%\end{itemize}"+"\n")
        wbtitle.write(r"\rule{\linewidth}{1pt}"+"\n")
        wbtitle.write(r"\vfill"+"\n")
        wbtitle.write(r"\centering"+"\n")
        wbtitle.write(r"\includegraphics[height=1.65cm]{\compilationpath/logos/\groupelogo}"+"\n")
        wbtitle.write(r"\end{document}"+"\n")
        wbtitle.close()

    def doMakeCatalogue(self):
        """Creates a pdf containing all exercises. Each exercise is always followed by its solution"""
        afile = "/tmp/catalogue.tex"
        self.__serie=0
        if os.path.isdir("Catalogue"):
            shutil.rmtree("Catalogue")
        os.mkdir("Catalogue")
        catalogue = open(afile, 'w') #use open(file 'a') for appending to a given file
        self.__createHeader(catalogue, [])
        catalogue.write(r'\renewcommand{\exercice}[1]{\subsection*{Problem: #1}}'+"\n")
        catalogue.write(r'\renewcommand{\solution}[1]{\subsection*{Solution: #1}}'+"\n")
        catalogue.write(r'\renewcommand{\question}[1]{\subsubsection*{#1}}'+"\n")
        catalogue.write(r''+"\n")
        catalogue.write(r'\makeatletter'+"\n")
        catalogue.write(r'\renewcommand{\section}{\@startsection{section}{3}{2pt}{12pt}{10pt}{\center \huge \sffamily \bfseries}}'+"\n")
        catalogue.write(r'\renewcommand{\thesection}{(\roman{section})}'+"\n")
        catalogue.write(r'\renewcommand{\thesubsection}{(\roman{subsection})}'+"\n")
        #catalogue.write(r'\begin{latexonly}'+"\n")
        #catalogue.write(r'\floatstyle{boxed}'+"\n")
        #catalogue.write(r'\restylefloat{figure}'+"\n")
        #catalogue.write(r'\end{latexonly}'+"\n")
        exos = os.listdir(self.__exoDirName)
        #exos.sort()
        exos = self.natsort(exos)
        for exo in exos:
            if exo.find("ex") != -1:
                number = exo[2:]
                catalogue.write(r'\section*{Exercise '+number+'}'+"\n")
                catalogue.write(r'\renewcommand{\includepath}{\compilationpath/'+self.__exoDirName+'/ex'+number+'/latex/resources}'+'\n')
                #catalogue.write(r'\begin{graybox}'+"\n")
                #catalogue.write(r'\begin{minipage}[width=\linewidht]'+"\n")
                #catalogue.write(r'\pagecolor{gray}'+"\n")
                exo = open(os.path.join(os.path.join(self.__exoDirName, "ex"+number),"latex/exo"+number+".tex"), 'r')
                for line in exo:
                    catalogue.write(line)
                #catalogue.write(r'\pagecolor{white}'+"\n")
                #catalogue.write(r'\end{graybox}'+"\n")
                #catalogue.write(r'\end{minipage}'+"\n")
                exo.close()
                catalogue.write(r'\renewcommand{\includepath}{\compilationpath/'+self.__exoDirName+'/ex'+number+'/latex/resources}'+'\n')
                solution = open(os.path.join(os.path.join(self.__exoDirName, "ex"+number),"latex/exo"+number+"sol.tex"), 'r')
                for line in solution:
                    catalogue.write(line)
                solution.close()
                if self.__smscaddClearPage:
                    catalogue.write("\clearpage")
        self.__createFooter(catalogue)
        catalogue.close()
        outputDir = "Catalogue"
        self.__doLatex(afile, outputDir)

    def __doPreviewExercice(self):
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

    def previewExercice(self, _exonumber):
        self.__exercise = _exonumber
        self.__doPreviewExercice()

    def __doPreviewSolution(self):
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

    def previewSolution(self, _exonumber):
        self.__exercise = _exonumber
        self.__doPreviewSolution()     
        
    def __doLatex(self, _texFile,  _outputDir,  _doBibTex=True):
        self.__log.info("Running latex in %s on file %s", _outputDir, _texFile)
        self.__log.debug("LaTeX command is: latexmk -pdf -silent -outdir={:s} {:s}".format(_outputDir,  _texFile))
        status = subprocess.call(["latexmk", "-pdf",  "-silent",   "-outdir="+_outputDir,   _texFile], cwd="./", stdout=open("/dev/null", 'w'))
        self.__log.info("Compilation succeded "+_texFile)
        # Alternatively use latexmk -c -jobname=texFile plus remove the *.tex file
        tmpfiles = os.listdir(_outputDir)
        tmpfiles.sort()
        basename = os.path.split(_texFile)[1].split(".")[0]
        self.__log.debug("Basename "+basename)
        for dafile in tmpfiles:
            if dafile.find(".pdf")==-1 and dafile.find(basename)!=-1:
                os.remove(os.path.join(_outputDir, dafile))

    def __doLatex2(self, _texFile, _outputDir, _doBibTex=True):
        #deprecated
        #self.__log.info("Running latex in %s on file %s", outputDir, texFile)
        #self.__log.info("Running latex in %s on file %s", os.getcwd(), texFile)
        self.__log.info("Compiling %s",  _texFile)
        self.__log.debug("Compile command is: pdflatex -output-directory="+_outputDir+" -halt-on-error "+_texFile)
        auxFile = os.path.split(_texFile)[1].split(".")[0]+'.aux'
        logFile = os.path.split(_texFile)[1].split(".")[0]+'.log'
        recompile = True
        counter = 0
        while recompile and counter < 5:
            recompile=False
            counter+=1
            self.__log.debug("Running latex for the "+str(counter)+" time")
            status = subprocess.call(["pdflatex", "-output-directory="+_outputDir, "-halt-on-error",  _texFile], cwd="./", stdout=open("/dev/null", 'w'))
            if _doBibTex:
                self.__log.debug("Running bibtex for the "+str(counter)+" time")
                bibstatus = subprocess.call(["bibtex", os.path.join(_outputDir,auxFile)], cwd="./", stdout=open("/dev/null", 'w'))
                self.__log.debug("Running latex again to reflect BibTeX changes")
                status = subprocess.call(["pdflatex", "-output-directory="+_outputDir, "-halt-on-error",  _texFile], cwd="./", stdout=open("/dev/null", 'w'))
                status = subprocess.call(["pdflatex", "-output-directory="+_outputDir, "-halt-on-error",  _texFile], cwd="./", stdout=open("/dev/null", 'w'))
            else:
                bibstatus = 0
            if status != 0:
                self.__log.error("Compilation error occured. Try executing by hand pdflatex -output-directory="+_outputDir+" -halt-on-error "+_texFile)
                exit(1)
            if bibstatus !=0:
                self.__log.error("Compilation error occured. Try executing by hand bibtex "+os.path.join(_outputDir,auxFile))
                exit(1)
            log = open(os.path.join(_outputDir, logFile), 'r')
            for line in log:
                for msg in self.__latex_recompile_messages:
                    if msg in line:
                        recompile=True
                        self.__log.debug("Need to recompile "+_texFile)
                        self.__log.debug(line)
                        break
            log.close()
        self.__log.debug("Compilation succeded "+_texFile)
        tmpfiles = os.listdir(_outputDir)
        tmpfiles.sort()
        basename = os.path.split(_texFile)[1].split(".")[0]
        for dafile in tmpfiles:
            if dafile.find(".pdf")==-1 and dafile.find(basename)!=-1:
                os.remove(os.path.join(_outputDir, dafile))

    def __doUpdateBibTex(self):
        """Updates the last visited date of the nocite bibtex items"""
        self.__log.info("Updating BibTex Last visited time stamp")
        bibtex = open(self.__smscbibtex, 'r')
        bibtexnew = open (os.path.join("/tmp/", self.__smscbibtex), 'w')
        start = False
        year = datetime.datetime.now().strftime("%Y")
        month = datetime.datetime.now().strftime("%b")
        day = datetime.datetime.now().strftime("%d")
        dateExpr = re.compile(r"\{\d*\}\{\w+?\}\{\d*\}")
        for line in bibtex:
            if line.find('biburl{') != -1 and start:
                partitions = dateExpr.split(line)
                self.__log.debug(partitions)
                bibtexnew.write(partitions[0]+'{'+day+'}{'+month+'}{'+year+'}'+partitions[1])
            else:
                bibtexnew.write(line)
            for cite in self.__noCiteList:
                if line.find(cite) != -1:
                    start=True
            if line.find("}") != -1 and line.find('},')==-1:
                start=False
        bibtex.close()
        bibtexnew.close()
        shutil.copy(os.path.join("/tmp/", self.__smscbibtex), self.__smscbibtex)

    def __cleanTempFiles(self):
        if self.__keepTempFiles:
            return
        self.__log.info("Removing temp files")
        tmpfile = os.listdir('/tmp')
        tmpfile.sort()
        for dafile in tmpfile:
            if dafile.find("serie") != -1 or dafile.find("solution") != -1 or dafile.find("wbtitle")!= -1:
                self.__log.debug("Removing /tmp/"+dafile)
                os.remove('/tmp/'+dafile)
    
    def __myZip(self, _directory, _destZipFile, _zipPrefix="."):
        """Zips a directory recursively to the destination zipfile"""
        self.__log.debug("Zipping directory: "+_directory+" to "+_destZipFile)
        if len(os.listdir(_directory)) == 0:
            return
        zippedDir = zipfile.ZipFile(_destZipFile, 'w')
        def zipTreeWalker(args, dirname, fnames):
            theZipArch = args[0]
            root = args[1]
            prefix = args[2]
            fnames.sort()
            for dafile in fnames:
                dafile = os.path.join(dirname, dafile)
                archiveName = dafile[len(os.path.commonprefix((root, dafile)))+1:]
                archiveName = os.path.join(prefix, archiveName)
                if not os.path.isdir(dafile):
                    theZipArch.write(dafile, archiveName)
        for root, dirs, files in os.walk(_directory, topdown=True):
            dirs[:] = [d for d in dirs if d not in self.__exclude_from_zip]
            zipTreeWalker([zippedDir, _directory, _zipPrefix], root, files)

    def __myTar(self, _directory, _destTarFile, _tarPrefix="."):
        """Creates a tar.gz file of a directory to destTarFile"""
        exclude_list = ['nbproject', 'dist', 'reports', 'bin', 'doc', 'group.properties']
        def needToExclude(f):
            return f.endswith('.svn') or f.endswith('.git') or f.endswith('~') or f in exclude_list
        
        self.__log.debug("Tar.gz - ing "+_directory+" to "+_destTarFile+". Using python tar")
        containingFolder = os.path.basename(_destTarFile)[:os.path.basename(_destTarFile).find(".")]
        tarTempName = "/tmp/tmp.tar.gz"
        files = os.listdir(_directory)
        if len(files) == 0:
            return
        tarArchive = tarfile.open(tarTempName, 'w:gz')
        cwd = os.getcwd()
        os.chdir(os.path.join(cwd, _directory))
        self.__log.debug('Available files for tar: '+str(files))
        for f in files:
            tarArchive.add(f,  exclude=needToExclude)
        os.chdir(cwd)
        if len(tarArchive.getmembers()) == 0: 
            return
        tarArchive.close()
        
        shutil.move(tarTempName, _destTarFile)
        return _destTarFile

    def cleanDSStore(self, _folder):
        def cleaner(_currdir, _dirs, _files):
            for item in _files:
                if item.find("DS_Store") != -1:
                    self.__log.debug("removing "+_currdir+"/"+item)
                    os.remove(os.path.join(_currdir, item))
        for root, dirs, files in os.walk(_folder):
            #self.cleanDSStore(root, dirs, files)
            cleaner(root, dirs, files)

    def natsort(self, _list):
        self.__log.debug("Will filter the list "+str(_list))
        filteredList = [elem for elem in _list if not elem.startswith(".")]
        self.__log.debug('Filtered list: '+str(filteredList))
        # decorate
        tmp = [ (int(re.search('\d+', i).group(0)), i) for i in filteredList ]
        self.__log.debug('Tmp list: '+str(tmp))
        tmp.sort()
        #   undecorate
        return [ i[1] for i in tmp ]
    
    def __doCheckInstall(self):
        """Verifies if all needed packets are installed"""
        self.__log.info("Checking dependencies")
        missingProgs = list()
        try:
            subprocess.check_call("which gs", shell=True, stdout=open("/dev/null", 'w'))
        except subprocess.CalledProcessError as e:
            self.__log.error("Did not found ghostscript (gs)")
            self.__log.debug(e)
            missingProgs.append("Ghostscript (gs)")
        try:
            subprocess.check_call("which pdflatex", shell=True, stdout=open("/dev/null", 'w'))
        except subprocess.CalledProcessError as e:
            self.__log.error("Did not found pdflatex")
            self.__log.debug(e)
            missingProgs.append("PdfLaTeX")
        try:
            subprocess.check_call("which tar", shell=True, stdout=open("/dev/null", 'w'))
        except subprocess.CalledProcessError as e:
            self.__log.error("Did not found Tar utility")
            self.__log.debug(e)
            missingProgs.append("Tar")
        try:
            if len(missingProgs) !=0:
                raise checkInstallException(missingProgs)
        except checkInstallException as x:
            self.__log.error("Please ensure that the needed utilities ("+x.missing+") are installed and on the $PATH")
            sys.exit(-1)

    def usage(self):
        print ('Usage:')
        print (os.path.basename(sys.argv[0])+' [option] <command>') #sys.argv[0]
        print ('\033[1;33mWhere option is one of:\033[0m')
        print ('    -e for specifying an exercise')
        print ('    -s for specifying a serie')
        print ('    -u for updating/or not last visited date in bibtex')
        print ('    -k for keeping/or not unzipped files')
        print ('    -t for keeping temporary files in /tmp')
        print ('    -z for doing a zip file')
        print ('\033[1;33mWhere command is one of:\033[0m')
        print ('    make-new-exercise.........................Creates a new exercise structure')
        print ('    build-serie (-s option mandatory).........Builds all for the specified serie and packs it for moodle')
        print ('    build-all-series..........................Builds all available series and packs them for moodle')
        print ('    make-workbook.............................Creates one big pdf wich contains all concatenated series')
        print ('    make-catalogue............................Creates a pdf containing all exercices')
        print ('    preview-exercise (-e option mandatory)....Previews the specified exercise')
        print ('    preview-solution (-e option mandatory)....Previews the solution for the specified exercise')

    def getArguments(self, argv):
        # Parse the command line options
        if len(argv) == 0:
            self.usage()
            sys.exit(3)
        try:
            options, args = getopt.getopt(argv, "e:s:huktz", ["make-new-exercise", "build-serie", "build-all-series", "make-workbook", "make-catalogue", "preview-exercise", "preview-solution", "--help"])
        except getopt.GetoptError:
            self.usage()
            sys.exit(2)
        self.cleanDSStore("./")
        self.__doCheckInstall()
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
        self.__log.debug("Parsing arguments")
        for option, arg in options:
            self.__log.debug("Passed options are  \"%s\"  and args are \"%s\"", option, arg)
            if option in ["--make-new-exercise"]:
                self.__log.info("Creating a new Exercice")
                self.doCreateNewExercice()
                break
            elif option in ["--build-serie"]:
                if self.__serie == -1:
                    self.__serie = int(raw_input ("Which serie do you want to build? "))
                self.__log.info("Building Serie %s", self.__serie)
                self.__doBuildSerie()
                if self.__smscdozipfiles:
                    self.__log.info("Zipping "+self.__smscmoodleOutputDir+str(self.__serie)+" into "+self.__smscmoodleOutputDir+str(self.__serie)+'.zip')
                    self.__myZip(self.__smscmoodleOutputDir+str(self.__serie), self.__smscmoodleOutputDir+str(self.__serie)+'.zip', self.__smscmoodleOutputDir+str(self.__serie))
                    if self.__smscremoveUnzipped:
                        shutil.rmtree(self.__smscmoodleOutputDir+str(self.__serie))
                    break
            elif option in ["--build-all-series"]:
                self.__log.info("Building All Available Series")
                self.doBuildAllSeries()
                if self.__smscdozipfiles:
                    self.__log.info("Zipping "+self.__smscmoodleOutputDir+" into "+self.__smscmoodleOutputDir+'.zip')
                    self.__myZip(self.__smscmoodleOutputDir, self.__smscmoodleOutputDir+'.zip', self.__smscmoodleOutputDir)
                    if self.__smscremoveUnzipped:
                        shutil.rmtree(self.__smscmoodleOutputDir)
                    break
            elif option in ["--make-workbook"]:
                self.__log.info("Building Workbook")
                self.doMakeWorkbook()
                break
            elif option in ["--make-catalogue"]:
                self.__log.info("Creating Catalogue of available Exercices")
                self.doMakeCatalogue()
                break
            elif option in ["--preview-exercise"]:
                if self.__exercise == -1:
                    self.__exercise = int(raw_input ("Which exercise do you want to preview? "))
                self.__log.info("Previewing exercise %s", self.__exercise)
                self.__doPreviewExercice()
                break
            elif option in ["--preview-solution"]:
                if self.__exercise == -1:
                    self.__exercise = int(raw_input ("Which solution do you want to preview? "))
                self.__log.info("Previewing solution %s", self.__exercise)
                self.__doPreviewSolution()
                break
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
