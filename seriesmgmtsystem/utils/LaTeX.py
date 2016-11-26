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
#   you may not use this _file except in compliance with the License.                                           #
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
import sys
if float(sys.version[:3])<3.0:
    import ConfigParser
else:
    import configparser as ConfigParser
from pkg_resources import resource_filename
from os.path import dirname, join

class LaTeX:
    
    def __init__(self, serie):
        """initialization stuff"""
        smsConfig = ConfigParser.SafeConfigParser()
        smsConfig.read([join(resource_filename(__name__, 'data'), 'lecture.cfg'), "lecture.cfg"])


        self.__name = smsConfig.get("Lecture", "name")
        self.__lecturer = smsConfig.get("Lecture", "lecturer")
        self.__year = smsConfig.get("Lecture", "year")
        self.__exercisetext = smsConfig.get("Lecture", "exercisetext")
        self.__solutiontext = smsConfig.get("Lecture", "solutiontext")
        self.__contenttext = smsConfig.get("Lecture", "contenttext")
        self.__headertitle = smsConfig.get("Lecture", "headertitle")
        self.__bibtex = smsConfig.get("Lecture", "bibtex")
        self.__noCiteList = smsConfig.get("Lecture", "nocite").split(",")
        self.__unilogo = smsConfig.get("Logo", "unilogo")
        self.__groupelogo = smsConfig.get("Logo", "groupelogo")
        self.__pdfkeyword = smsConfig.get("PDF", "pdfkeyword")
        self.__pdftitle = smsConfig.get("PDF", "pdftitle")
        self.__pdfauthor = smsConfig.get("PDF", "pdfauthor")

        self.__serie = serie
        self.__log = logging.getLogger('seriesManagementSystem')


    def createHeader(self, _file, titles, isSolution=False):
        _file.write(r'\documentclass[francais,a4paper]{article}'+"\n")
        _file.write(r'\usepackage{sms}'+"\n")
        _file.write(r"\newcommand{\compilationpath}{./}"+"\n")
        _file.write(r'\newcommand{\prof}{'+self.__lecturer+'}'+"\n")
        _file.write(r'\newcommand{\course}{'+self.__name+'}'+"\n")
        _file.write(r'\newcommand{\theyear}{'+self.__year+'}'+"\n")
        _file.write(r'\newcommand{\exercisetext}{'+self.__exercisetext+'}'+"\n")
        if isSolution:
            solutionText = self.__solutiontext
        else:
            solutionText = ''
        _file.write(r'\newcommand{\solutiontext}{'+solutionText+'}'+"\n")
        _file.write(r'\newcommand{\thecontent} {\sffamily\bfseries '+self.__contenttext+':}'+"\n")
        _file.write(r'\newcommand{\theheadertitle}{'+self.__headertitle+'}'+"\n")
        _file.write(r'\newcommand{\unilogo}{'+self.__unilogo+'}'+"\n")
        _file.write(r'\newcommand{\groupelogo}{'+self.__groupelogo+'}'+"\n")
        #afile.write(r"\input{\compilationpath/exercicepreamble}"+"\n")
        _file.write(r"% Number of the serie"+"\n")
        _file.write(r"\newcommand{\exercisenb}{"+str(self.__serie)+"}"+"\n")
        _file.write(r"\newcommand{\includepath}{\compilationpath}"+"\n")
        _file.write(r'\hypersetup{pdftitle={'+self.__pdftitle+'},pdfauthor={'+self.__pdfauthor+'},pdfkeywords={'+self.__pdfkeyword+"}}\n")
        _file.write(r"\begin{document}"+"\n")
        _file.write(r"\input{\compilationpath/captionnames}"+"\n")
        _file.write(r"% Header of the exercise:"+"\n")
        _file.write(r"\exheader"+"\n")

        if len(titles) != 0:
            _file.write(r"% Content of the exercise, topics"+"\n")
            _file.write(r"\content{"+"\n")
            _file.write(r"\begin{itemize}"+"\n")
            for title in titles:
                _file.write(r'\item '+title+'\n')
            _file.write(r'\end{itemize}'+'\n')
            _file.write(r'}'+'\n')
    
    def createFooter(self, _file):
        for bib in self.__noCiteList:
            _file.write(r'\nocite{'+bib+'}\n')
        _file.write(r'\bibliography{bibdb}'+'\n')
        _file.write(r'\bibliographystyle{plain}'+'\n')
        _file.write(r'\end{document}'+'\n')



    def makeWorkBookTitlePageHeader(self, _file):
        _file.write(r"\documentclass[francais,a4paper]{article}"+"\n")
        _file.write(r"\newcommand{\compilationpath}{./}"+"\n")
        _file.write(r'\newcommand{\groupelogo}{'+self.__groupelogo+'}'+"\n")
        _file.write(r"\usepackage{graphicx}"+"\n")
        _file.write(r"\usepackage{palatino}"+"\n")
        _file.write(r"%\usepackage[french]{babel}"+"\n")
        _file.write(r"\usepackage[utf8]{inputenc}"+"\n")
        _file.write(r"\usepackage{ae, pslatex}    % Joli output en PDF"+"\n")
        _file.write(r"%\usepackage{graphics}          % Manipulation de boîtes et importation de graphismes."+"\n")
        _file.write(r"%\usepackage[dvips]{graphicx}   %"+"\n")
        _file.write(r"\usepackage[T1]{fontenc}"+"\n")
        _file.write(r"\begin{document}"+"\n")
        _file.write(r"\pagestyle{empty}"+"\n")
        _file.write(r"\vspace{-1cm}"+"\n")
        _file.write(r"\begin{center}"+"\n")
        _file.write(r"\begin{Huge}"+"\n")
        _file.write(r"{\sf "+self.__name+" }"+"\n")
        _file.write(r"\end{Huge}"+"\n")
        _file.write(r"\vspace{0.4cm}%"+"\n")
        _file.write(r"\begin{huge}"+"\n")
        _file.write(r"Workbook ("+self.__year+")"+"\n")
        _file.write(r"\end{huge}"+"\n")
        _file.write(r"\end{center}"+"\n")
        _file.write(r"\rule{\linewidth}{1pt}"+"\n")
        _file.write(r"\vspace{1cm}"+"\n")

    def printWorkBookTitlePageFooter(self, _file):
        _file.write(r"%\end{itemize}"+"\n")
        _file.write(r"\rule{\linewidth}{1pt}"+"\n")
        _file.write(r"\vfill"+"\n")
        _file.write(r"\centering"+"\n")
        _file.write(r"\includegraphics[height=1.65cm]{\compilationpath/logos/\groupelogo}"+"\n")
        _file.write(r"\end{document}"+"\n")
        
