# Series Management System

A utility to manage series

# Installation

## Final installation

from a terminal launch

    sudo python setup.py install --record files.txt

this will compile and install the project to the pyhton libraries (eg. /usr/local/lib/python2.7/dist-packages/XWoT_Model_Translator-1.1-py2.7.egg). Furthermore it will install three scripts in /usr/local/bin/:
* physical2virtualEntities
* model2Python
* model2WADL
The configuration and logging.conf are copied into /etc/Model2WADL/ but it is possible to overwrite them either by placing a file with the same name (but prefixed with a dot eg. .logging.conf) in the user home directory or a file with the same name in the current working directory.

## Development installation

from a terminal launch

    sudo python setup.py develop --record files.txt
    
does the same as before but, uses links instead of copying files.

# Clean Working directory

To clean the working directory
    
    sudo python setup.py clean --all
    sudo rm -rf build/ dist/ XWoT_Model_Translator.egg-info/ files.txt


# Uninstall

## Method 1
    cat files.txt |sudo xargs rm -rf

## Method 2

First find the installed package with pip and the uninstall it

    ~/Documents/Programming/Python/Model2WADL [master|✚ 1…1] 
    12:13 $ pip freeze |grep XWot*
    3:XWoT-Model-Translator==1.1
    ~/Documents/Programming/Python/Model2WADL [master|✚ 1…1] 
    12:13 $ sudo pip uninstall XWoT-Model-Translator
    Uninstalling XWoT-Model-Translator:
      /Library/Python/2.7/site-packages/XWoT_Model_Translator-1.1-py2.7.egg
      /usr/local/bin/model2Python
      /usr/local/bin/model2WADL
      /usr/local/bin/physical2virtualEntities
    Proceed (y/n)? y
        Successfully uninstalled XWoT-Model-Translator
     ~/Documents/Programming/Python/Model2WADL [master|✚ 1…1] 
    12:13 $
     
 