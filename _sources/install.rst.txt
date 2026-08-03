Installation
====================

From Download
--------------

The simplest way to use *seriesManagementSystem* is to download the packaged *pex* file from `sms`_ and put it somewhere on the path like ``/usr/local/bin/``or ``/usr/local/share/bin``or ``~/.local/bin/`` and make it executable,

From this point on, the binary can be executed by calling the *pex* file directly. 

.. only:: builder_html

    Download files directly from here:

    * :download:`seriesManagementSystem_.pex <../dist/seriesManagementSystem_.pex>` For Python > 3.10

From pip
---------

Simply run::

    pipx install seriesManagementSystem


From Sources
-------------

Create a Virtual Environment
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To not tamper the system wide Python installation first create a new virtual environment and activate it

  python3 -m venv venv-312
  source venv-312/bin/activate.bash


Final installation
^^^^^^^^^^^^^^^^^^

From a terminal launch::

    pip install .

This will compile and install the project to the python libraries (eg. ``/usr/local/lib/python3.12/site-packages/seriesManagementSystem-1.3.1.dev13.dist-info``). Furthermore, it will install a script in ``/usr/local/bin/``:
* seriesManagementSystem

Upon the first start a copy of a pristine application and logging configuration are created in the user's home directory ``~/.SeriesManagementSystem/``. From this point on configuration files are read from this location. It is however possible to overwrite them either by placing a file with the same name (but prefixed with a dot eg. ``.logging.conf``) in the current working directory.

Development installation
^^^^^^^^^^^^^^^^^^^^^^^^

from a terminal launch::

    pip install -e .

does the same as before but, uses links instead of copying files.

Code Guideline Checking
^^^^^^^^^^^^^^^^^^^^^^^^

To check the code guidelines run::

    flake8 --max-line-length=88 --statistics --extend-ignore=E501,E203,W503 --select=E,W,F .


After fixing the issues you can reformat the code with::

    black .

Run type checks
^^^^^^^^^^^^^^^^^^^^^^

To run type checks on the code base use::

    mypy src tests

All in one command
^^^^^^^^^^^^^^^^^^^^^^

To run code guideline checks and type checks in one command use::

    tox -e lint,type


Clean Working directory
^^^^^^^^^^^^^^^^^^^^^^^^

To clean the working directory::

    python setup.py clean --all
    rm -rf build/ dist/


Release Software
-----------------

Version numbers are derived from the git history with `setuptools_scm <https://github.com/pypa/setuptools-scm>`_: Likely `python -m setuptools_scm` prints the current version. It's a mix from the version of the last git tag plus the `dev` suffix with a number indicating the distance to the last git tag. If the command is called on a commit with a git tag then it just takes that tag.

The releasing itself is done with `twine <https://twine.readthedocs.io/en/latest/index.html>`_

* Build the software: `python -m build` (if not using `tox`) for creating the packages
* Check if everything is ready for deplyoment: `python -m twine check dist/*`
* Upload artifacts: `python -m twine upload --repository pypitest --verbose dist/*`



Uninstall
----------

Method 1 (pipx)
^^^^^^^^^^^^^^

If the package was installed with ``pipx`` simply run::

    pipx uninstall seriesManagementSystem


Method 2 (pip)
^^^^^^^^^^^^^^

If the package was installed with ``pip`` simply run::

    pip uninstall seriesManagementSystem


Building the documentation locally
----------------------------------

To build the documentation follow these steps:

.. code-block:: bash

    $ git clone https://github.com/digsim/seriesManagementSystem/
    $ cd seriesManagementSystem
    $ python3 -m venv venv-312
    $ source venv-312/bin/activate.bash
    $ pip install -r requirements_docs.txt
    $ cd docs
    $ make html

You can now open the output from ``_build/html/index.html``. To build the
presentation-version use ``make presentation`` instead of ``make html``. You
can open the presentation at ``presentation/index.html``.


.. _`sms`: https://www.andreas-ruppen.ch/
