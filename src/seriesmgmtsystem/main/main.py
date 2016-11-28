from __future__ import unicode_literals
import sys
import shutil
import signal
import logging.config
import os
import pkgutil
import pkg_resources
import six

if float(sys.version[:3])<3.0:
    import ConfigParser
else:
    import configparser as ConfigParser
try:
    from subprocess import DEVNULL # py3k
except ImportError:
    import os
    DEVNULL = open(os.devnull, 'wb')
from os.path import join, expanduser



class Main(object):

    def __init__(self, configDirName, configName, logFileName):
        """
        Constructor.

        :param configDirName: Name of the directory where the configuration is stored.
        :param configName: Name of the configuration file.
        :param logFileName: Name of the log file.
        """
        self.original_sigint = signal.getsignal(signal.SIGINT)
        self.__CONFIG_DIR = pkgutil.get_loader('seriesmgmtsystem').get_filename()
        self.__CONFIG_DIR = os.path.dirname(self.__CONFIG_DIR)
        self.__CONFIG_DIR = os.path.join(self.__CONFIG_DIR, 'etc')
        self.__USER_CONFIG_DIR = expanduser('~/.'+configDirName)

        self.__configName = configName
        self.__logFileName = logFileName
        self._checkUserConfigFiles()
        self.version = pkg_resources.require('seriesmgmtsystem')[0].version

        logging.basicConfig(level=logging.DEBUG)
        logging.config.fileConfig(
            [join(self.__CONFIG_DIR, 'logging.conf'), join(self.__USER_CONFIG_DIR, 'logging.conf'), 'logging.conf'],
            defaults={'logfilename': os.path.join(self.__USER_CONFIG_DIR, self.__logFileName)})
        self.__log = logging.getLogger('Tube4Droid')

        # Configure several elements depending on config file
        if float(sys.version[:3])<3.2:
            self.config = ConfigParser.SafeConfigParser()
        else:
            self.config = ConfigParser.ConfigParser()
        self.config.read([join(self.__CONFIG_DIR, self.__configName), join(self.__USER_CONFIG_DIR, self.__configName), self.__configName])


    def main(self):
        """This is the main entry point. Call this function at the end of getArguments"""
        signal.signal(signal.SIGINT, self._exit_gracefully)
        self.doWork()

    def doWork(self):
        """
        This the main method doing some actual work. This function needs to be overwritten by the <code>mainImpl.py</code> class.

        :return: void
        """
        return

    def getArguments(self, argv):
        """
        Do the argument parsing. This function needs to be overwritten by the <code>mainImpl.py</code> class.

        :param argv: array of command line arguments
        :return: void
        """
        return

    def _checkPythonVersion(self):
        """
        Checks the pyhton version. Does nothing more than log the used version.

        :return: void.
        """
        self.__log.debug('Using Python '+sys.version[:3])

    def _checkUserConfigFiles(self):
        """
        Verifies that the necessary configuration directory and files exist. If not, they are created from skeleton
        files and a message is printed indicating the user that he shall first adapt the default configuration.

        :return: void.
        """
        printWarningAndAbort=False
        if not os.path.exists(self.__CONFIG_DIR):
            print('Could not find initial configuration skeletons. Aborting')
            return
        if not os.path.exists(self.__USER_CONFIG_DIR):
            print('User config dir does not exist. Creating '+self.__USER_CONFIG_DIR)
            os.mkdir(self.__USER_CONFIG_DIR)
            printWarningAndAbort=True
        if not os.path.exists(join(self.__USER_CONFIG_DIR, 'logging.conf')):
            print('Copying default logging conf to '+self.__USER_CONFIG_DIR)
            shutil.copy(join(self.__CONFIG_DIR, 'logging.conf'), join(self.__USER_CONFIG_DIR, 'logging.conf'))
        if not os.path.exists(join(self.__USER_CONFIG_DIR, self.__configName)):
            print('No application specific config file found. Creating '+self.__configName+' in '+self.__USER_CONFIG_DIR )
            shutil.copy(join(self.__CONFIG_DIR, self.__configName), join(self.__USER_CONFIG_DIR, self.__configName))
            printWarningAndAbort = True
        if printWarningAndAbort:
            print('Created initial configuration files in '+ self.__USER_CONFIG_DIR)
            print('Please edit '+ self.__USER_CONFIG_DIR+'/'+self.__configName)
            sys.exit(1)

    def _exit_gracefully(self, signum, frame):
        """
        Helper function for signal handling. Responsible for handling CTRL-C and abort the execution.
        Prior to aborting, the user is asked if the really wants to interrupt.

        :param signum:
        :param frame:
        :return: void
        """
        # restore the original signal handler as otherwise evil things will happen
        # in raw_input when CTRL+C is pressed, and our signal handler is not re-entrant
        signal.signal(signal.SIGINT, self.original_sigint)
        if float(sys.version[:3]) < 3.0:
            real_raw_input = raw_input
        else:
            real_raw_input = input

        try:
            if real_raw_input('\nReally quit? (y/n)> ').lower().startswith('y'):
                sys.exit(1)
        except KeyboardInterrupt:
            print('Ok ok, quitting')
            sys.exit(1)

        # restore the exit gracefully handler here
        signal.signal(signal.SIGINT, self._exit_gracefully)

