=======================
Pytheon command scripts
=======================

pytheon-admin
=============

``bin/pytheon-admin`` command deploy your application in *pytheon* hosting environment.

.. code-block:: sh

    $ Usage: pytheon-admin [options]

    Options:
      --version             show program's version number and exit
      -h, --help            show this help message and exit
      -i INTERPRETER, --interpreter=INTERPRETER
                            Default to: /usr/bin/python
      -d SOURCE, --deploy=SOURCE
                            Default to $SOURCE if exist.
      -b BRANCH, --branch=BRANCH
                            Default to $BRANCH if exist
      -a APP_NAME, --app-name=APP_NAME
      --destroy=DESTROY     
      --host=HOST           
      -r ROOT, --root=ROOT  Default to ~/root/
      -e EGGS, --eggs=EGGS  Default to: ~/eggs/
      --develop=DEVELOP     Testing only
      --develop-dir=DEVELOP_DIR
                            Used for buildout:develop-dir. Default to $DEVELOP_DIR
                            if exist

Examples
========


