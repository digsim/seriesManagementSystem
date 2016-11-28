# Tube4Droid

A script to prepare Youtube videos for offline use in any podcatcher software.

This script downloads the specified youtube playlist (see {{playlist}} property into the directory specified in
{{mediadir}}. Once all videos downloaded, it creats an RSS feed out of these videos and save the resulting file
to the {{rssdir}} directory (which can be the same as the mediadir directory. Furhtermore, the script needs to know the
server uri (see {{serveruri}} property) from where the final RSS feed will be served.

## Installation

## From pip

Simply run
```
pip install missingTVShows
```

## From Sources

### Final installation

From a terminal launch
```
sudo python setup.py install --record files.txt
```
this will compile and install the project to the pyhton libraries (eg. /usr/local/lib/python3.5/site-packages/tube4droid-0.9-py3.5.egg). Furthermore it will install a script in /usr/local/bin/:
* tube4droid

The basic configuration and logging.conf are copied into /etc/Tube4Droid/. Upon the first start a copy of this directory is created in the user's home directory ~/.Tube4Droid/. From this point on configuration files are read from this location. It is however possible to overwrite them either by placing a file with the same name (but prefixed with a dot eg. .logging.conf) in the user home directory or a file with the same name in the current working directory.

### Development installation

from a terminal launch
```
sudo python setup.py develop --record files.txt
```
does the same as before but, uses links instead of copying files.

### Clean Working directory

To clean the working directory
```
sudo python setup.py clean --all
sudo rm -rf build/ dist/ feedcreator.egg-info/ files.txt
```

# Uninstall

## Method 1
```
pip uninstall tube4droid
```

## Method 2 (if installed from sources)
```
cat files.txt |sudo xargs rm -rf
```
## Method 3  (if installed from sources)

First find the installed package with pip and the uninstall it
```
✔ ~/Documents/Programming/Python/tube4Android [master|✚ 1]
19:02 $ pip3 freeze |grep feedcreator
feedcreator==0.9

✔ ~/Documents/Programming/Python/tube4Android [master|✚ 1]
19:02 $ sudo pip3 uninstall feedcreator
Uninstalling feedcreator-0.9:
  /usr/local/lib/python3.5/site-packages/feedcreator-0.9-py3.5.egg
Proceed (y/n)? y
  Successfully uninstalled feedcreator-0.9
✔ ~/Documents/Programming/Python/tube4Android [master|✚ 2]
19:03 $
```
# Configuration

Upon the first launch, the script creates the ~/.Tube4Droid/ directory containing:
* logging.conf where the logger is configured
* tube4droid.conf where the general configuration is stored. Adapt at least the <serveruri>, <mediadir>, <rssdir> and <playlist> properties to get started 

You need a running web server from which the dowloaded files can be saved later on. Therefore, the <mediadir> and <rssdir> properties could point to, for example, {{/var/www/rss/}} whereas  the <serveruri> could be {{http://example.com/rss}} given that the webserver is configured in such a way that this URI point to the {{/var/www/rss}} directory.

