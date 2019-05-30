=====
Tests
=====

Tests are developed using the
`Testinfra <https://testinfra.readthedocs.io>`__ package. The package
extends Pytest and provides a framework for writing Python tests to
verify the actual state of systems.

SLES Test Suite
===============

There is a suite of tests for SLES and openSUSE_Leap. It can be found
in the `GitHub repository
<https://github.com/SUSE-Enceladus/img-proof/tree/master/usr/share/lib/img_proof/tests>`__.

They are also packaged in the Open Build Service for openSUSE:

.. code-block:: console

   $ zypper ar http://download.opensuse.org/repositories/Cloud:/Tools/<distribution>
   $ zypper refresh
   $ zypper in python3-img-proof-tests

Test directories
================

The default locations for test files are locally in ~/img_proof/tests/ and
centralized in /usr/share/img_proof/tests. These locations can be overridden
in the config and/or command line arguments.

Test organization
=================

Tests can be organized in a directory structure:

::

   ~/img_proof/tests/:
     conftest.py
     test_image.py
     openSUSE:
       test_leap.py
       EC2:
         test_leap_ec2.py
       GCE:
       ...
     SLES:
       test_sles.py
       test_sles_sap.py
       EC2:
         test_sles_ec2.py
       ...

Additionally, test descriptions in YAML format can be used to organize
tests:

**test_leap_423.yaml.**

.. code-block:: yaml

   tests:
     - test_image
     - test_leap

Adding tests to command line args you simply drop the extension:

.. code-block:: shell

   $ img-proof test ... test_leap_423

This means there cannot be a name overlap with test files and/or test
descriptions.

Test descriptions can also include other descriptions:

**test_leap_423.yaml.**

.. code-block:: yaml

   tests:
     - test_image
     - test_leap
   include:
     - test_another_description

Test invocation
===============

To invoke a specific test the Pytest conventions can be used:

.. code-block:: console

   $ img-proof test ... test_leap_ec2::test-services-running-enabled

To run only one parameterized test append ids and use [ID]:

.. code-block:: python3

   @pytest.mark.parametrize("name", [
       ("cloud-init"),
       ("amazon-ssm-agent"),
   ], ids=['ci', 'ssm'])
   def test_leap_ec2():
     ...

.. code-block:: console

   $ img-proof test ... test_leap_ec2::test-services-running-enabled[ssm]

Failures
--------

By default all tests will run even with failure. Using the
``--early-exit`` option will halt test invocation at first failure.

`Incremental test
classes <http://pytest.org/dev/example/simple.html#incremental-testing-test-steps>`__
can be used to cause all subsequent tests to fail if the prev fails. To
prevent expected failures.

Custom Test Modules
===================

`Modules <http://testinfra.readthedocs.io/en/latest/modules.html>`__ are
provided for checking standard things such as packages, services, files,
etc.

Modules can be easily written or extended from using `Pytest
fixtures <https://docs.pytest.org/en/latest/fixture.html>`__. Any custom
modules reside in the conftest.py file inside the test directory:

.. code-block:: python3

   import pytest

   @pytest.fixture()
   def Echo(Command):
       def f(arg):
           return Command.check-output("echo %s", arg)
       return f


   @pytest.fixture()
   def CheckRepo(File):
       def f(repo, name):
           repo = File('/etc/zypp/repos.d/' + repo + '.repo')
           tests = [repo.exists,
                    repo.contains('enabled=1'),
                    repo.contains('name=%s' % name)]
           return all(tests)
       return f

Useful Links
============

For more info on writing tests see the
`Testinfra <http://testinfra.readthedocs.io/en/latest/>`__ and
`Pytest <https://docs.pytest.org/en/latest/contents.html>`__
documentation.
