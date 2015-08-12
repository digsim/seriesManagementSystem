# Series Management System

A utility to manage series

# Installation

## Final installation

from a terminal launch

    sudo python setup.py install --record files.txt

this will compile and install the project to the Python libraries (eg. /usr/local/lib/python2.7/dist-packages/Series_Management_System-1.1-py2.7.egg). Furthermore it will install a script in /usr/local/bin/:
* seriesManagementSystem
The configuration and logging.conf are copied into /etc/SeriesManagementSystem/ but it is possible to overwrite them either by placing a file with the same name (but prefixed with a dot eg. .logging.conf) in the user home directory or a file with the same name in the current working directory.

## Development installation

from a terminal launch

    sudo python setup.py develop --record files.txt
    
does the same as before but, uses links instead of copying files.

# Clean Working directory

To clean the working directory
    
    sudo python setup.py clean --all
    sudo rm -rf build/ dist/ Series_Management_System.egg-info/ files.txt


# Uninstall

## Method 1
    cat files.txt |sudo xargs rm -rf

## Method 2

First find the installed package with pip and the uninstall it

    ~/SMS [master|✚ 1…1] 
    12:13 $ pip freeze |grep Series*
    4:Series-Management-System==1.1
    ~/SMS [master|✚ 1…1] 
    12:13 $ sudo pip uninstall Series-Management-System
    Uninstalling Series-Management-System:
      /Library/Python/2.7/site-packages/Series_Management_System-1.1-py2.7.egg
      /usr/local/bin/seriesManagementSystem
    Proceed (y/n)? y
        Successfully uninstalled Series-Management-System
     ~/SMS [master|✚ 1…1] 
    12:13 $
     

# Exercises

The exercises are made of two parts:
* a folder containing all exercises.
* a configuration file for each series of exercises and

By default the folder containing all exercises is Exercices. For the system to work this folder has to follow a strict hierarchy. It contains different folders, all named "ex" plus a number, eg. ex1, ex2, ... ex10 etc. Each of these folders contain only one exercise, its solution plus additional material (which will be zipped) to distribute with the series, respectively with the solution. The structure is as follows:
 
    ~:$ ls -lR Exercices/ex1
    total 0
    drwxr-xr-x  4 ruppena  staff   136B Feb 10 12:22 code/
    drwxr-xr-x  3 ruppena  staff   170B Mar  3 14:04 latex/
    
    Exercices/ex1/code:
    total 0
    drwxr-xr-x  4 ruppena  staff   238B Mar  4 15:04 donne/
    drwxr-xr-x  9 ruppena  staff   476B Mar  4 15:45 solution/
    
    Exercices/ex1/code/donne:
    total 72
    -rw-r--r--  1 ruppena  staff   1.1K Feb 10 12:22 build.properties
    -rw-r--r--  1 ruppena  staff    24K Mar  4 15:04 build.xml
    ...
    ...
    ...
    
    Exercices/ex1/code/solution:
    total 80
    -rw-r--r--  1 ruppena  staff   1.1K Feb 10 12:22 build.properties
    -rw-r--r--  1 ruppena  staff    24K Mar  4 15:04 build.xml
    ...
    ...
    ...
    
    Exercices/ex1/latex:
    total 16
    -rw-r--r--  1 ruppena  staff   1.0K Mar  3 14:04 exo.tex
    -rw-r--r--  1 ruppena  staff    66B Feb 10 12:22 exosol.tex
    drwxr-xr-x  4 ruppena  staff   136B Feb 10 12:22 resources/
    
    Exercices/ex1/latex/resources:
    total 0
    drwxr-xr-x  2 ruppena  staff   102B Feb 10 12:22 code_tex/
    drwxr-xr-x  2 ruppena  staff   306B Feb 10 12:22 figures/
    
    Exercices/ex1/latex/resources/code_tex:
    total 8
    -rw-r--r--  1 ruppena  staff   1.0K Feb 10 12:22 listing.tex
    
    Exercices/ex1/latex/resources/figures:
    total 1360
    -rw-r--r--  1 ruppena  staff   9.0K Feb 10 12:22 inherit.png
    
Each exercise is made of two folders: code containing additional material to be distributed and latex containing the latex code to generate the serie.
    
Additional material to be distributed in zipped form with the series needs to be placed in a subfolder code/donnee whereas distributed material to be distributed with the solution needs to be placed in a subfolder code/solution.

The exercise latex code is in a file ex.tex where number must be the same as used in the folder containing the exercise. The same applies for the solution, which is written in a file called exosol.tex. 

Resources used for the latex code are stored in a subfolder resources. This folder contains a folder, figures to store images which are included with

    \includegraphics[height=7cm]{\compilationpath/Exercices/ex3/latex/resources/figures/inherit.png}
    

    

By default the properties for a serie are stored in the folder Series_properties. A typical config file looks like:

    [Serie]
    titles: Classes et ADT, Programmation orient\'ee objets en Java - types statique et dynamique, Java: h\'eritage - polymorphisme - interfaces - ...
    exo-numbers: 1,2,3

It contains only one section: Serie with two keys. The titles key defines the topics of the serie and is a comma separated list. In the final document this will produce an itemize in the serie header. The second property exo-number defines which exercices are selected for this serie. The number references the last (numbered) part of one exercise folder.