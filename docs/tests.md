---
layout: default
title: Tests
navigation_weight: 4
---

Tests are developed using the
[Testinfra](https://testinfra.readthedocs.io) package. The package
extends Pytest and provides a framework for writing Python tests to
verify the actual state of systems.

Test directories
================

The default locations for test files are locally in \~/ipa/tests/ and
centralized in /usr/share/ipa/tests. These locations can be overridden
in the config and/or command line arguments.

Test organization
=================

Tests can be organized in a directory structure:

    ~/ipa/tests/:
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

**test\_leap\_423.yaml.**

```yaml
tests:
  - test_image
  - test_leap
```

Adding tests to command line args you simply drop the extension:

```shell
$ ipa test ... test_leap_423
```

This means there cannot be a name overlap with test files and/or test
descriptions.

Test descriptions can also include other descriptions:

**test\_leap\_423.yaml.**

```yaml
tests:
  - ...
include:
  - test_another_description
```

Test invocation
===============

To invoke a specific test the Pytest conventions can be used:

    test_leap_ec2::test-services-running-enabled

To run only one parameterized test append ids and use \[ID\]:

**test\_leap\_ec2.py.**

```python
@pytest.mark.parametrize("name", [
    ("cloud-init"),
    ("amazon-ssm-agent"),
], ids=['ci', 'ssm'])
def test_leap_ec2():
  ...
```

```shell
$ ipa test ... test_leap_ec2::test-services-running-enabled[ssm]
```

Failures
--------

By default all tests will run even with failure. Using the
`--early-exit` option will halt test invocation at first failure.

[Incremental test
classes](http://pytest.org/dev/example/simple.html#incremental-testing-test-steps)
can be used to cause all subsequent tests to fail if the prev fails. To
prevent expected failures.

Custom Test Modules
===================

[Modules](http://testinfra.readthedocs.io/en/latest/modules.html) are
provided for checking standard things such as packages, services, files,
etc.

Modules can be easily written or extended from using [Pytest
fixtures](https://docs.pytest.org/en/latest/fixture.html). Any custom
modules reside in the conftest.py file inside the test directory:

**conftest.py.**

```python
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
```

Useful Links
============

For more info on writing tests see the
[Testinfra](http://testinfra.readthedocs.io/en/latest/) and
[Pytest](https://docs.pytest.org/en/latest/contents.html) documentation.
