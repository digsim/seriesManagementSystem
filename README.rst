==========================================================
SeriesManagementSystem
==========================================================

The `sms`_  - SeriesManagmentSystem - Is a tool to manage and distributes exercises to students. The exercises
are prepared indiviually, each with its own resources (like source code) and its solution. From there it is possible
to creates series by combining different exercises together on the fly. Such Series can then be compiled to PDF files (plus additional resources which get zipped)


----

    :Homepage: https://github.com/digsim/seriesManagementSystem
    :Code: https://github.com/digsim/seriesManagementSystem
    :Mailing list: https://github.com/digsim/seriesManagementSystem
    :Dependencies: `pytvdbapi`_ `colorama`_ `sqlalchemy`_ `sqlalchemy-utils`_ `six`_ `mysqlclient`_  `progressbar2`_ and `setuptools`_
    :Compatible with:  2.7 and 3.3+
    :License: `APACHE`_

----


.. image:: https://travis-ci.org/digsim/seriesManagementSystem.svg?branch=master
    :target: https://travis-ci.org/digsim/seriesManagementSystem


Roadmap
=======

- 2.0: Progress bar,
- 2.1: More fancy stuff,


.. _`pytvdbapi`: http://pypi.python.org/pypi/pytvdbapi
.. _`sms`: https://github.com/digsim/seriesManagementSystem
.. _`colorama`: https://pypi.python.org/pypi/colorama
.. _`sqlalchemy`: https://pypi.python.org/pypi/SQLAlchemy
.. _`sqlalchemy-utils`: http://pypi.python.org/pypi/sqlalchemy-utils
.. _`mysqlclient`: http://pypi.python.org/pypi/sqlalchemy-utils
.. _`progressbar2`: http://pypi.python.org/pypi/sqlalchemy-utils
.. _`six`: http://pythonhosted.org/six/
.. _`setuptools`: http://pypi.python.org/pypi/setuptools
.. _`APACHE`: http://www.apache.org/licenses/LICENSE-2.0.txt


Test Coverage Report
====================

Output from coverage test::

    py35 runtests: commands[1] | coverage report
    Name                                                Stmts   Miss  Cover
    -----------------------------------------------------------------------
    src/seriesmgmtsystem/__init__.py                        2      0   100%
    src/seriesmgmtsystem/main/__init__.py                   5      5     0%
    src/seriesmgmtsystem/main/main.py                      77     77     0%
    src/seriesmgmtsystem/main/mainImpl.py                  98     98     0%
    src/seriesmgmtsystem/sms/__init__.py                    0      0   100%
    src/seriesmgmtsystem/sms/serieManagementSystem.py     298    221    26%
    src/seriesmgmtsystem/utils/LaTeX.py                    98     86    12%
    src/seriesmgmtsystem/utils/Utils.py                   154    135    12%
    src/seriesmgmtsystem/utils/ZipUtils.py                 55     45    18%
    src/seriesmgmtsystem/utils/__init__.py                  0      0   100%
    -----------------------------------------------------------------------
    TOTAL                                                 787    667    15%
