Running tests
=============

Make sure you have the latest bootstrap before running the tests.

Note
-----

If you encouter a setuptools issue the sollution I found is installing a new setupools::

    $ wget https://bitbucket.org/pypa/setuptools/raw/0.8/ez_setup.py
    $ sudo /usr/bin/python ez_setup.py

Running tests
-------------

::

    python bootstrap.py
    bin/buildout
    bin/test
