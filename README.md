# Series Management System

This is a tool to automatically generate series based on individual exercises. For this, individual exercises are stored in the `Exercises` folder (configurable, see `exoDirName` option), each in  separate sub-folders named `exXX` where `XX` are digits.

Series are defined using `cfg` files, one for each series. The `cfg` files contains information like which exercises to include. Using LaTeX, the system compiles different exercises into series.

## Installation

### Requirements

Install LaTeX on you system. Make sure the commands `pdflatex`, `bibtex` and `latexmk` are available on the `$PATH` of your operating system. Furthermore the script sometimes uses either `gs` or `pdftk` (configurable, see `usepdftk` option) to combine several PDF documents.

### User Installation
from a terminal launch
```
ruppena@tungdil:~$ sudo pip install seriesManagementSystem
```
this will compile and install the project to the Python libraries (eg. `/usr/local/lib/python2.7/dist-packages/Series_Management_System-1.1-py2.7.egg`). Furthermore it will install a script in `/usr/local/bin/`:
* seriesManagementSystem
The configuration and logging.conf are copied into `/etc/SeriesManagementSystem/` but it is possible to overwrite them either by placing a file with the same name (but prefixed with a dot eg. `.logging.conf`) in the user home directory or a file with the same name in the current working directory.

### Developer Installation
from a terminal launch
```
ruppena@tungdil:~$ git clone https://github.com/digsim/seriesManagementSystem.git
ruppena@tungdil:~$ cd seriesManagementSystem
ruppena@tungdil:~$ sudo python setup.py install --record files.txt
```

#### Clean Working directory

To clean the working directory

    sudo python setup.py clean --all
    sudo rm -rf build/ dist/ Series_Management_System.egg-info/ files.txt

### Bash Completion Installation

If your system supports bash-completion, it can be activated to have option completion for this script. The file `serieManagementSystem-completion.bash` is copied during the installation into the folder `/usr/local/etc/bash_completion.d/` make sure this folder is activated as bash-completion folder in your `.bashrc`, `.bash_login` or `.profile`

```
if ! shopt -oq posix; then
  if [ -f /usr/local/etc/bash-completion ]; then
    . /usr/local/etc/bash-completion
fi
```

### Uninstall
from a terminal launch
```
ruppena@tungdil:~$ sudo pip uninstall seriesManagementSystem
ruppena@tungdil:~$ sudo rm -rf /Library/Python/2.7/site-packages/seriesManagementSystem*
```
this will remove the package and any associated artifacts.

## Utilization

* To get help type following command in the console:
```
ruppena@tungdil:~$ seriesManagementSystem --help
```
* To create a new exercise empty structure type:
```
ruppena@tungdil:~$ seriesManagementSystem --make-new-exercise
```

* To build a new serie:
```
ruppena@tungdil:~$ seriesManagementSystem --build-serie -s XX
```
where `XX` is the number identifying a `serieXX.cfg` file in the `Series_properties` folder.

* To create all the series
```
ruppena@tungdil:~$ seriesManagementSystem --build-all-series
```
This compiles all defines series in the `Series_properties` folder.

* To generate a quick pdf preview for a given exercise
```
ruppena@tungdil:~$ seriesManagementSystem --preview-exercise -e XX
```
where `XX` identifies on of the `exXX` folders of the `Exercises` folder. The PDF is opened with the viewer specified in the `opencmd` option.

* To generate a quick pdf preview for a given exercise solution
```
ruppena@tungdil:~$ seriesManagementSystem --preview-solution -e XX
```
where `XX` identifies on of the `exXX` folders of the `Exercises` folder. The PDF is opened with the viewer specified in the `opencmd` option.

* To create a single PDF containing all series and the associated solutions in the defined order.
```
ruppena@tungdil:~$ seriesManagementSystem --make-workbook
```
* To create a single PDF containing the collection of all defined exercises
```
ruppena@tungdil:~$ seriesManagementSystem --make-catalogue
```

## Serie Definition

By default the properties for a serie are stored in the folder `Series_properties` (configurable, see `seriesConfigDir` option). A typical config file looks like:

    [Serie]
    titles: Classes et ADT, Programmation orient\'ee objets en Java - types statique et dynamique, Java: h\'eritage - polymorphisme - interfaces - ...
    exo-numbers: 1,2,3

It contains only one section: `Serie` with two keys.
* The `titles` key defines the topics of the serie and is a comma separated list. In the final document this will produce an itemize in the serie header.
* The second property `exo-number` defines which exercises are selected for this serie. The number references the last (numbered) part of one exercise folder.

## Configuration

The general configuration is hold in a file called `lecture.cfg`. It contains a bunch of key values which are grouped into 4 sections: `Config`, `Lecture`, `Logo` and `PDF `.

The `Config` sections defines various folders like the one containing the individual exercises, the output directory, whether `pdftk` or `gs` is used for PDF concatenation or whether the generated files are zipped or not.

The `Lecture` folder defines some strings specific for each lecture like its name and the name of the lecturer. It also contains strings for naming the series and the solutions.

The `Logo` part defines the logos which are shown on the left and right of the header.

The `PDF` part contains options used by LaTeX when creating the PDF file.

Additionally, the generated `lecture.cfg` file is fully documented.

## Exercise Folder Structure

By default the folder containing all exercises is `Exercices` (configurable, see `exoDirName` option). For the system to work, this folder needs to contain a strict hierarchy. It contains several folders, all named "ex" plus a number, eg. `ex1`, `ex2`, ... `ex10` etc. Each of these folders contain only one exercise, its solution plus additional material (which will be zipped) to be distributed together with the series and the solution respectively. The structure is as follows:

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

Each exercise is made of two folders: `code` containing additional material to be distributed and `latex` containing the latex code to generate the exercise.

Additional material to be distributed in zipped form with the exercise needs to be placed in a subfolder `code/donnee` whereas distributed material to be distributed with the solution needs to be placed in a subfolder `code/solution`.

The exercise latex code is in a file `ex.tex` where number must be the same as used in the folder containing the exercise. The same applies for the solution, which is written in a file called `exosol.tex`.

Resources used for the latex code are stored in a subfolder `resources`. This folder contains a folder, `figures` to store images which are included with

    \includegraphics[height=7cm]{\includepath/figures/inherit.png}

Furthermore, it contains a subfolder `code` used to store source code which is later included into the LaTeX source with

    \lstinputlisting{\includepath/code_tex/ADT.java}
