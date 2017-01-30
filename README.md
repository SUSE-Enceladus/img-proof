# ipa

ipa (Image Proofing App)

## Overview

ipa provides a Python API and command line utility to test images in the
Public Cloud (AWS, Azure, GCE, etc.).

**CLI**

The architecture for the command line utility leverages the Click
library.

The CLI provides multiple subcommands to initiate image testing:

* `ipa test`

 The test subcommand invokes a test suite on an image in the chosen public
 cloud environment. The image id, tests and provider are required arguments.
 See below for options:

  ```
  ipa test [OPTIONS] IMAGE_ID PROVIDER TESTS

  --host                  Use existing instance for tests (--host=10.10.0.1)
  -c, --cleanup           Whether to leave instance running after tests (y/n)
                          By default an instance will be deleted on success
                          and left running if there is a test failure.
  -p, --private-key-file  Private SSH key file
  -r, --region            Region of image
  -t, --type              Instance type to use for machine
  -u, --user              SSH user for instance

  -n, --name              Only run tests with string in name (-n STRING)
  -m, --mark              Run only marked tests (-m hpc)
  -s, --skip              Skip all marked tests (-s hpc) 

  --junitxml PATH         Location to store junit xml results
  --results PATH          Location to store test cmd output

  --maxfail               Terminate after n failures (--maxfail=2)
  -x                      Terminate test suite on first failure

  -v, --verbose           Enables verbose mode
  --version               ipa version
  -h, --help              Show this message and exit.

  Example:
  ipa test -v -x --junitxml=results.xml ami1234 aws test_aws_leap.py
  ```

  The SSH user, SSH private key file, region and type are all optional
  and will override the values found in config respective of CSP. E.g.
  for ec2 the ~/.ec2utils.conf file will be default.

* `ipa results`

 The results subcommand displays the test results information. The
 path to the results xml is required.

  ```
  ipa results [OPTIONS] RESULTS

  -v, --verbose        Display the verbose test output
  -h, --help           Show this message and exit.

  Example:
  ipa results -v results.xml
  ```

  The default location for results files is ~/ipa/results/ and the files
  are encoded with the day/time of execution and found in their respective
  CSP folder. E.g. for ec2 the results would be found at ~/ipa/results/ec2/.
  And the files would look like SLES-12-SP2-{datetime}.results. Junit style
  results would be the same with an extension of .junit. If multiple tests are
  run with a comma separated list the tests results will all be appended to the
  same results file.

* `ipa list`

  The list subcommand displays the available tests.
  ```
  ipa list FILE[OPTIONAL]

  The FILE argument is optional and can be used to display tests
  from a specific test file or entire directory.

  -v, --verbose
  -h, --help

  Examples:
  ipa list
  ipa list ~/ipa/tests/SLES12SP1/
  ipa list ~/ipa/tests/SLES12SP1/test_sles_12_sp1_hpc.py
  ```

  The list subcommand will return a list of test files if a directory is
  passed in as the argument. Or it will return a list of all available tests
  if a specific test file is passed in. Using the verbose option with a dir
  as the argument or no arguments will list every test file and all tests the
  file invokes including any inherited tests.

  Example output:
  ```
  $ ipa list -v

  test_image.py
    test_packages[local-python-virtualenv-13]
    test_echo[local]
    test_packages[local-python-2.7]
  leap/test_leap.py
    test_repos[local-repo-oss-openSUSE-Leap-42.1-Oss]
    test_packages[local-python-virtualenv-13]
    test_echo[local]
    test_repos[local-repo-non-oss-openSUSE-Leap-42.1-Non-Oss]
    test_packages[local-python-2.7]
  leap/test_leap_aws.py
    test_repos[local-repo-oss-openSUSE-Leap-42.1-Oss]
    test_services_running_enabled[local-cloud-init]
    test_packages[local-python-virtualenv-13]
    test_echo[local]
    test_repos[local-repo-non-oss-openSUSE-Leap-42.1-Non-Oss]
    test_services_running_enabled[local-amazon-ssm-agent]
    test_packages[local-python-2.7]
  ```

* Using click an invalid argument yields a message as such:
  ```
  Error: No such command "invalidcmd".
  ```

**Config**

The framework config is ini format ~/ipa/.config. Anything specific to
the test framework can be found in this config.

Any settings relating to a CSP can be found in it's respective config. For
example any ec2 information can be found in ~/.ec2utils.conf.

```
[default]
tests=~/ipa/tests/
results=~/ipa/results/
```

**API**

The API used by CLI or used independently, is structured with a base class
ipa.py:TestProvider. This contains the functionality required to run tests
and collect the test results. These methods are implemented the same for
any cloud provider while the specific tests and test configuration may change.

This base class is extended for each provider to implement specific methods
for manipulating the test instance. This includes launch, start, stop, and
terminate.

**Tests**

Tests are developed using the testinfra package. The package extends
pytest and provides a framework for writing Python tests to verify the actual
state of systems. <sup>[[1]](#1)</sup> The default location for test files is
~/ipa/tests/.

**Writing Tests**

Tests can be organized in a directory structure:

```
~/ipa/tests/:
  conftest.py           # Pytest custom modules and config goes here
  test_image.py         # Generic tests for all images
  leap_leap_422:
    test_leap_422.py        # Generic leap tests
    EC2:
      test_leap_422_ec2.py  # Specific EC2 tests for leap images 
    GCE:
    ...
  SLES12SP1:
    test_sles_12_sp1.py
    test_sles_12_sp1_sap.py    # Can import SLES12SP1 tests
    EC2:
      test_sles_12_sp1_sap_ec2.py
    ...
  SUMA3:
    ...
```

A test file can inherit tests by importing another file. For example the
test_leap_422.py file would import test_image.py to include all generic
image tests. An example for this structure would be similar to the
files below:

```python
# test_leap_422_ec2.py #
import pytest
from test_leap_422 import *           # Import all generic leap tests

@pytest.mark.parametrize("name", [
    ("cloud-init"),
    ("amazon-ssm-agent"),
])
def test_services_running_enabled(Service, name):
    service = Service(name)
    assert service.is_running
    assert service.is_enabled
```

The file which contains specific leap 42.2 tests for EC2 images inherits
all tests specific to the leap 42.2 image.

```python
# test_leap_422.py #
import pytest
from test_image import *          # Import all generic image tests

@pytest.mark.parametrize("repo,name", [
    ("repo-oss", "openSUSE-Leap-42.1-Oss"),
    ("repo-non-oss", "openSUSE-Leap-42.1-Non-Oss"),
])
def test_repos(CheckRepo, repo, name):
    assert CheckRepo(repo, name)
```

The leap 42.2 test file inherits all generic image tests.

```python
# test_image.py #
import pytest

@pytest.mark.parametrize("name,version", [
    ("python-virtualenv", "13"),
    ("python", "2.7"),
])
def test_packages(Package, name, version):
    assert Package(name).is_installed
    assert Package(name).version.startswith(version)


def test_echo(Echo):
    assert Echo("Hello") == 'Hello'
```

Thus when invoking the test_leap_422_ec2.py file the following tests are
run:

```
$ ipa test -v test_leap_422_ec2.py -p key_file -u ec2-user

..test_packages[paramiko://0.0.0.0-python-virtualenv-13] PASSED
..test_echo[paramiko://0.0.0.0] PASSED
..test_repos[paramiko://0.0.0.0-repo-oss-openSUSE-Leap-42.1-Oss] PASSED
..test_services_running_enabled[paramiko://0.0.0.0-cloud-init] PASSED
..test_packages[paramiko://0.0.0.0-python-2.7] PASSED
..test_repos[paramiko://0.0.0.0-repo-non-oss-openSUSE-Leap-42.1-Non-Oss] PASSED
..test_services_running_enabled[paramiko://0.0.0.0-amazon-ssm-agent] PASSED
```

All 7 tests from the three test files are ran when testing the 42.2 EC2 image.

**Test invocation**

To invoke the entire test suite for a Leap image in EC2 the test_leap_42.2_ec2.py
target would be used.

To invoke a specific test the Pytest conventions can be used:
```
test_leap_422_ec2.py::test_services_running_enabled.
```

To run only one parameterized test append ids and use [local-ID]:
```
@pytest.mark.parametrize("name", [
    ("cloud-init"),
    ("amazon-ssm-agent"),
], ids=['ci', 'ssm'])


test_leap_422_ec2.py::test_services_running_enabled[local-ssm]
```

Tests and classes of tests can be marked and run independent of other tests:
```
@pytest.mark.hpc
def test_something():
  ...

-m hpc option will run only tests marked as hpc.
```

Markers can be used to run all combinations of tests. <sup>[[2]](#2)</sup>
For example an environment marker could be used to run all tests plus the
specified environment such as hpc. As compared to the above example which
will only run tests marked as hpc.

**Failures**

By default all tests will run even with failure. Using the -x option will
halt test invocation at first failure.

Incremental test classes can be used to cause all subsequent tests to fail
if the prev fails. To prevent expected failures. <sup>[[3]](#3)</sup>

And a set number of failures can be chosen prior to halting. Using
--maxfail=2 will halt after two failures.

**Custom Test Modules**

Modules are provided for checking standard things such as packages,
services, files, dirs etc. Modules can be easily written and extended
from to provide custom modules such as CheckRepo. Any custom modules could
be written in conftest.py in the same dir and would be resolved by
pytest automagically:

```python
# conftest.py #
import pytest

@pytest.fixture()
def Echo(Command):
    def f(arg):
        return Command.check_output("echo %s", arg)
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

**Pytest**

Any other functionality provided by pytest for writing the tests can be used.
See pytest docs for more information. <sup>[[4]](#4)</sup>

**Summary**

The stack in use:
- testinfra (infrastructure testing)
- click (cli)
- ini (config)
- boto3 (EC2 instances)
- Python Azure SDK (Azure instances)
- Google Cloud SDK (GCE instances)

**Links**

<a name="1">1</a>: https://testinfra.readthedocs.io<br />
<a name="2">2</a>: http://doc.pytest.org/en/latest/example/markers.html<br />
<a name="3">3</a>: http://pytest.org/dev/example/simple.html#incremental-testing-test-steps<br />
<a name="4">4</a>: http://doc.pytest.org/en/latest/<br />
<a name="5">5</a>: http://doc.pytest.org/en/latest/usage.html#calling-pytest-from-python-code<br />

