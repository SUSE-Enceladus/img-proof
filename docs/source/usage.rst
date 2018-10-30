=====
Usage
=====

IPA provides two entry points, a command line interface and a controller class
that can be used directly from Python code.

CLI
---

The command line interface is written using the `Click`_ package and has a
documented :doc:`api`.

.. _Click: https://click.palletsprojects.com/en/7.x/

Testing an image with CLI
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: console

   > ipa test -i {image-id} \
     -a {account} \
     -d openSUSE_Leap \
     --early-exit \
     --no-cleanup \
     --no-color \
     --debug \
     ec2 test_image

   Starting instance
   Running tests /home/{user}/ipa/tests/test_image.py
   PASSED tests=1|pass=1|fail=0|error=0

Verbosity
~~~~~~~~~

As seen in the example the CLI output verbosity can be controlled via options:

**\\-\\-debug**
    Display debug level logging to console. Including full stack trace
    if there is an exception.

**\\-\\-verbose**
    (Default) Display logging info to console.

**\\-\\-quiet**
    Silence logging information on test run.

Cleanup
~~~~~~~

By default the instance will be terminated if all tests pass. If a test
fails the instance will remain running for debuggin purposes. This
behavior can be configured with the ``--cleanup`` and ``--no-cleanup``
flags.

**\\-\\-cleanup**
    Instance will always be terminated.

**\\-\\-no-cleanup**
    Instance will always remain running.

ANSI Style
~~~~~~~~~~

By default the command line output will be colored. To disable color
output use the ``--no-color`` option.

Early Exit
~~~~~~~~~~

The early exit option will stop the test run on the first failure.
``--early-exit`` is passed to Pytest as ``-x``.

See `Pytest docs`_ for more info.

.. _Pytest docs: https://docs.pytest.org/en/latest/usage.html#stopping-after-the-first-or-n-failures

Requirements and external test injection
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Using the ``--inject`` option; packages, archives and files can be
injected on the test instance. This also provides the ability to install
packages in an existing repository and run commands on the test
instance.

The following sections may be provided in a YAML style config
file. Each section can be a single item or a list of items. All files
are copied and extracted to the default SSH location for the test
instance. This is generally the user’s home directory.

**inject_packages**
    an rpm path or list of rpm paths which will be copied and installed on
    the test instance.

**inject_archives**
    an archive or list of archives which will be copied and extracted on the
    test instance.

**inject_files**
    a file path or list of file paths which will be copied to the test
    instance.

**execute**
    a command or list of commands to run on the test instance.

**install**
    a package name or list of package names to install from an existing repo
    on the test instance.

The order of processing for the sections is as follows:

#. inject_packages
#. inject_archives
#. inject_files
#. execute
#. install

**Example**
^^^^^^^^^^^

**testing_injection.yaml.**

.. code-block:: yaml

   inject_packages: /home/user/test.noarch.rpm
   inject_archives: /home/user/test.tar.xz
   inject_files: /home/user/test.py
   install:
     - python3
     - python3-Django
   execute: python test.py

.. code-block:: console

   > ipa test ... --inject testing_injection.yaml

Code
----

**IPA** can also be imported and invokedd directly in Python 3 code through
the controller class. It is insalled as a Python site package and can be
imported as follows:

.. code-block:: python3

   from ipa.ipa_controller import test_image

   status, results = test_image(
       provider,
       access_key_id,
       ...
       storage_container,
       tests
   )

See :doc:`modules/ipa.ipa_controller` for specific methods that can be
invoked.
