from .main import Main
import argparse
from seriesmgmtsystem.sms.serieManagementSystem import SMS
from seriesmgmtsystem.utils import Utils, ZipUtils
from seriesmgmtsystem.utils.LaTeX import *


class MainImpl(Main):

    def __init__(self):
        """Constructor"""
        self.__configDirName = "seriesmgmtsystem"
        self.__configName = 'seriesmgmtsystem.conf'
        self.__logFileName = 'seriesmgmtsystem.log'

        super(MainImpl, self).__init__(self.__configDirName, self.__configName, self.__logFileName)
        self.__log = logging.getLogger('Tube4Droid')
        #self.__playlist = self.config.get('Config', 'playlist')


        self.__args = ''


    def getArguments(self, argv):
        """
        Parses the command line arguments.

        :param argv: array of command line arguments
        :return: void
        """
        self._checkPythonVersion()
        parser = argparse.ArgumentParser(prog='seriesManagementSystem',
                                         description='Series Management System.',
                                         epilog='%(prog)s {command} -h for help on individual commands')
        parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + self.version)
        subparsers = parser.add_subparsers(help='commands', dest='command')
        newExoParser = subparsers.add_parser('make-new-exercise', help='Creates a new Exercise')
        allSeriesParser = subparsers.add_parser('build-all-series', help='Compiles all availalbe series into one PDF per Serie')
        workbookParser = subparsers.add_parser('make-workbook', help='Creates a workbook of all series for a given year')
        newExoParser = subparsers.add_parser('make-catalogue', help='Creates a PDF catalog of all available Exercises')
        buildSerieParser = subparsers.add_parser('build-serie', help='Compiles one Serie into a PDF (including its solution)')
        previewExoParser = subparsers.add_parser('preview-exercise', help='Quick Compiles one exercise into a PDF')
        previewSolParser = subparsers.add_parser('preview-solution', help='Quick Compiles one solution into a PDF')
        newLectureParser = subparsers.add_parser('make-new-lecture', help='Creates a new Lecture')
        newExoParser = subparsers.add_parser('make-new-exercise', help='Creates a new Exercise')

        bibtexParser = parser.add_mutually_exclusive_group(required=False)
        zipParser = parser.add_mutually_exclusive_group(required=False)
        keepTmpParser = parser.add_mutually_exclusive_group(required=False)
        unzippedParser  = parser.add_mutually_exclusive_group(required=False)
        bibtexParser.add_argument("--updatebibtex", help="force updating last visited date in bibtex", required=False, dest='updateBibTex', action='store_true', default=None)
        bibtexParser.add_argument("--no-updatebibtex", help="forbid updating last visited date in bibtex", required=False,
                                  dest='updateBibTex', action='store_false', default=None)
        zipParser.add_argument("--keepunzipped", help="keep unzipped files", required=False, dest='keepUnzipped', action='store_true', default=None)
        zipParser.add_argument("--no-keepunzipped", help="discard unzipped files", required=False, dest='keepUnzipped',
                               action='store_false', default=None)
        keepTmpParser.add_argument("--keeptemp", help="keeping temporary files in /tmp", required=False,
                            dest='keepTemp', action='store_true', default=None)
        keepTmpParser.add_argument("--no-keeptemp", help="discard temporary files in /tmp", required=False,
                                   dest='keepTemp', action='store_false', default=None)
        unzippedParser.add_argument("--dozip", help="create a zip file", required=False,
                            dest='doZip', action='store_true', default=None)
        unzippedParser.add_argument("--no-dozip", help="don't create any zip files", required=False,
                                    dest='doZip', action='store_false', default=None)

        buildSerieParser.add_argument('-s', '--serie', dest='serie', required=True, help='Specify the serie to compile')
        previewExoParser.add_argument('-e', '--exo', dest='exercise', required=True, help='Specify the exercise to compile')
        previewSolParser.add_argument('-e', '--exo', dest='exercise', required=True,
                                      help='Specify the exercise to compile')
        newLectureParser.add_argument('-l', '--lecture', dest='lecture', required=True,
                                      help='Specify the lecture to create')



        if len(sys.argv) == 1:
            parser.print_help()
            sys.exit(1)
        args = parser.parse_args(argv)
        self.__args = args


        self.main()

        sys.exit(0)

    def doWork(self):
        """Overwrites the main"""
        Utils.cleanDSStore("./")
        Utils.doCheckInstall()
        command = self.__args.command
        updateBibTex = self.__args.updateBibTex
        keepUnzipped = self.__args.keepUnzipped
        keepTemp = self.__args.keepTemp
        doZip = self.__args.doZip
        if command == 'make-new-exercise':
            self.__log.info("Creating a new Exercice")
            sms = SMS(updateBibTex, keepUnzipped, keepTemp, doZip)
            sms.createNewExercice()
        elif command == 'build-all-series':
            self.__log.info("Building All Available Series")
            sms = SMS(updateBibTex, keepUnzipped, keepTemp, doZip)
            sms.buildAllSeries()
            sms.doZip()
        elif command == 'make-workbook':
            self.__log.info("Building Workbook")
            sms = SMS(updateBibTex, keepUnzipped, keepTemp, doZip)
            sms.makeWorkbook()
        elif command == 'make-catalogue':
            self.__log.info("Creating Catalogue of available Exercices")
            sms = SMS(updateBibTex, keepUnzipped, keepTemp, doZip)
            sms.makeCatalogue()
        elif command == 'build-serie':
            serie = self.__args.serie
            self.__log.info("Building Serie %s", serie)
            sms = SMS(updateBibTex, keepUnzipped, keepTemp, doZip, _serie=serie)
            sms.buildSerie()
            sms.doZip()
        elif command == 'preview-exercise':
            exercise = self.__args.exercise
            self.__log.info("Previewing exercise %s", exercise)
            sms = SMS(updateBibTex, keepUnzipped, keepTemp, doZip, _exercise=exercise)
            sms.previewExercice()
        elif command == 'preview-solution':
            exercise = self.__args.exercise
            self.__log.info("Previewing exercise %s", exercise)
            sms = SMS(updateBibTex, keepUnzipped, keepTemp, doZip, _exercise=exercise)
            sms.previewSolution()
        elif command == 'make-new-lecture':
            lecturename = self.__args.lecture
            sms = SMS(updateBibTex, keepUnzipped, keepTemp, doZip)
            sms.createNewLecture(lecturename)



if __name__ == "__main__":
    main = MainImpl()
    main.getArguments(sys.argv[1:])
