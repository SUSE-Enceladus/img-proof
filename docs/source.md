---
layout: default
title: Source
navigation_weight: 3
---

CLI
===

## ipa test

The test subcommand invokes a test suite on an image in the chosen
public cloud environment. The image id, tests and provider are required
arguments. See below for options:

```shell
$ ipa test --ssh-private-key /path/to/key -d SLES azure test_image
```

## ipa results

The results subcommand displays the test results information. The path
to the results xml is required.

```shell
$ ipa results -v
```

The default location for results files is \~/ipa/results/ and the files
are encoded with the timestamp of execution. For example, the results
for an image test in ec2 would be found at
\~/ipa/results/ec2/{imageId}/{instanceId}/{datetime}.results.

**Example results directory:**
    
    ec2/:
      ami-43243232/:
        i-3432r4324y3t2/:
          {datetime}.results
        i-432423j3j2432/:
          {datetime}.results

## ipa list

The list subcommand displays the available tests.

```shell
$ ipa list
test_broken
test_image
test_sles
```

The list subcommand will return a list of test files in the default test
directories. The verbose option will return a list of all available
tests in all test files.

```shell
$ ipa list -v
test_broken::test_broken
test_image::test_image
test_sles::test_sles
test_sles::test_sles_1
test_sles::test_sles_2
```

API
===

The API used by CLI or used independently, is structured with a base
class in ipa\_provider.py. This contains the functionality required to
run tests and collect the test results.

**ipa\_provider.py.**

```python
class IpaProvider(object):
...
```

The base class is extended for each provider to implement specific
methods for manipulating the test instance.

**ipa\_{cloud-provider}.py.**

```python
class {CloudProvider}Provider(IpaProvider):
...
```

The controller (ipa\_controller.py) provides methods for testing an
image, displaying available tests and/or test files and displaying
results of a previous test run. These methods provide a layer between
the CLI and the API. They also provide an entry point for using **ipa**
directly from code.

**ipa\_controller.py.**

```python
def test_image(self):
    """Creates a cloud provider instance and initiates testing."""

def list_tests(self):
    """Returns a list of test files and/or tests."""

def collect_results(self):
    """Returns the result (pass/fail) or verbose results."""
```
