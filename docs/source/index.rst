=======================
img-proof Documentation
=======================

.. image:: https://www.travis-ci.com/SUSE-Enceladus/img-proof.svg?branch=master
   :target: https://www.travis-ci.com/SUSE-Enceladus/img-proof

.. image:: https://img.shields.io/pypi/pyversions/img-proof.svg
   :target: https://pypi.org/project/img-proof/

.. image:: https://img.shields.io/pypi/l/img-proof.svg
   :target: https://pypi.org/project/img-proof/

.. toctree::
   :maxdepth: 3
   :hidden:

   Getting Started <start>
   Usage <usage>
   examples
   tests
   API <api>
   Modules <modules/img_proof>

.. image:: /_images/logo.png

**img-proof** (IPA) provides a command line utility to test images in the Public
Cloud (AWS, Azure, GCE, OCI, Aliyun, etc.).

About
-----

With **img-proof** you can now test custom images in a cloud framework agnostic way
with one tool and one API. **img-proof** supports the Fedora, openSUSE,
RHEL, and SLES distributions. It also supports the three largest
cloud frameworks (AWS, Azure and GCE). However, it is intended to be
distribution agnostic and framework transparent so both are easily
extensible.

Overview
--------

The goal of **img-proof** is to provide a unit test framework that can be used
to verify the actual state of custom public cloud images. To do this it
leverages two packages.

pytest
~~~~~~

Tests are written using the pytest framework.

The `pytest`_ framework makes it easy to write small tests, yet scales to
support complex functional testing for applications and libraries.

.. _pytest: https://docs.pytest.org/en/latest/

Testinfra
~~~~~~~~~~

Testinfra is a plugin for pytest which provides connection backends and
test modules such as File, Group, User, Package, Service, etc.

With `Testinfra`_ you can write unit tests in Python to test actual state
of your servers configured by management tools like Salt, Ansible,
Puppet, Chef and so on.

.. _Testinfra: https://testinfra.readthedocs.io/en/latest/

img-proof
~~~~~~~~~

**img-proof** leverages Testinfra as a unit test framework. It also provides
distribution classes and cloud framework classes.

Distribution Classes
^^^^^^^^^^^^^^^^^^^^

Classes can be used to provide distribution specific testing. This
includes tests such as soft reboot (e.g. "shutdown -r now") and update.

The current supported distributions are:

* Fedora
* openSUSE_Leap
* RHEL
* SLES


In addition to soft reboot, refresh and update there is a built in test for
hard reboot (framework reboot).

These tests are "synchronization points". The tests are built into each
distribution as the commands can be slightly different.

By default pytest does not guarantee the order of tests. However, there
are cases where this is ideal when testing images. For example you 
can run an update then do a reboot to ensure an instance starts properly.

A test suite such as ['test_soft_reboot', 'test_sles', 'test_update',
'test_hard_reboot', 'test_sles_ec2'] will be broken into five pytest
invocations:

Soft reboot, test_sles, update, hard reboot, test_sles_ec2

The order of tests is guaranteed and the results will be aggregated to
determine the status of a test run. If a test fails it will be re-run
up to the number of retries. The default is three times and this can be
configured with the **--retry-count** option.

Cloud Framework Classes
^^^^^^^^^^^^^^^^^^^^^^^

The cloud framework classes contain methods necessary to interact with
instances/images in a given cloud framework.

Some of the required methods for cloud framework classes include:

* Launch instances
* Terminate instances
* Get instance status
* Get instance info
* Stop/Start/Reboot instances

The implementations are dependent on each CSP API and require
the CSP credentials to perform the necessary operations.

The current supported CSPs are:

* Azure
* EC2
* GCE
* OCI
* SSH
* Aliyun

The SSH class is generic and can be used for any accessible instance
that is running. There are no credentials required except the instance
needs the proper SSH User and SSH Key configured for access.

The SSH class cannot be used to test hard reboot (framework reboot) or
to launch/start/stop/terminate instances.

Contributing
------------

Contributions to **img-proof** are welcome and encouraged. See `CONTRIBUTING`_ for
info on getting started.

.. _CONTRIBUTING: https://github.com/SUSE-Enceladus/img-proof/blob/master/CONTRIBUTING.md

Issues/Enhancements
-------------------

Please submit issues and requests to `Github`_.

.. _Github: https://github.com/SUSE-Enceladus/img-proof/issues

License
-------

Copyright (c) 2020 SUSE LLC.

Distributed under the terms of GPL-3.0+ license, see `LICENSE`_ for details.

.. _LICENSE: https://github.com/SUSE-Enceladus/img-proof/blob/master/LICENSE
