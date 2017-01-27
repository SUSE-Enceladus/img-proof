# ipa

ipa (Image Proofing App)

## Overview

### Design Discussion

ipa provides a Python API and command line utilities to test images in the
Public Cloud (AWS, Azure, GCE, etc.).

**Architecture**

**CLI**

The architecture for the command line utility will leverage the Click
library.

The CLI will provided multiple subcommands to initiate image testing:

* `ipa test`

 The test subcommand will invoke a test suite on an image in the chosen public
 cloud environment. The image id, tests and provider are required arguments.
 See below for options:

  ```
  ipa test [OPTIONS] IMAGE_ID PROVIDER TESTS

  --hosts                 List of hosts to run tests (--hosts=10.10.0.1)
  -r, --region            Region of image
  -s, --ssh-config PATH   SSH Config File
  -t, --type              Image type to use for machine

  -k                      Only run tests with string in name (-k STRING)
  -m                      Mark tests to run or skip (-m hpc or -m 'not hpc') 

  --junitxml PATH         Location to store junit xml results
  --results PATH          Location to store test cmd output

  --maxfail               Terminate after n failures (--maxfail=2)
  -x                      Terminate test suite on first failure

  -v, --verbose           Enables verbose mode
  --version               ipa version
  --help                  Show this message and exit.

  Example:
  ipa test -v -x --junitxml=results.xml ami1234 aws test_aws_leap.py
  ```

* `ipa results`

 The results subcommand will display the test results information. The
 path to the results xml is required.

  ```
  ipa results [OPTIONS] RESULTS

  -v, --verbose        Display the verbose test output
  --help               Show this message and exit.

  Example:
  ipa results -v results.xml
  ```

* Using click an invalid argument would yield a message as such:
  ```
  Error: No such command "invalidcmd".
  ```

**Config**

The framework config will be ini format ~/.ipa. Anything specific to
the test framework will be found in this config.

Any settings relating to a CSP will be in it's respective config. For example
any aws information will be found in ~/.aws/config or ~/.aws/credentials.

**API**

The API used by CLI or used independently, is structured with a base class
tester.py:TestProvider. This contains the functionality required to run tests
and collect the test results. These methods would be implemented the same for
any cloud provider while the specific tests and test configuration may change.

This base class is extended for each provider to implement specific methods
for manipulating the test instance. This includes launching an instance of the
image to be tested and start, stop, terminate the instance as well.

**Tests**

Tests will be developed using the testinfra package. The package extends
pytest and provides a framework for writing Python tests to verify the actual
state of systems. <sup>[[1]](#1)</sup> Testinfra is basically a Python
implementation of serverspec.

**Writing Tests**

Tests can be organized in a directory structure:

```
image_testing:
  conftest.py           # Pytest custom modules and config goes here
  test_image.py         # Generic tests for all images
  leap:
    test_leap.py        # Generic leap tests
    EC2:
      test_leap_ec2.py  # Specific EC2 tests for leap images 
    GCE:              
    ...
  SLES12:
    ...
  SLES4SAP:
    test_sles4sap.py    # Can import SLES12 tests from SLES12
    ...
  SUMA3:
    ...
```

Any test could be called directly from the tree and all parent tests would
run subsequently. An example for this structure would look like:

```python
# test_leap_ec2.py #
import pytest
from test_leap import *           # Import all generic leap tests

@pytest.mark.parametrize("name", [
    ("cloud-init"),
    ("amazon-ssm-agent"),
])
def test_services_running_enabled(Service, name):
    service = Service(name)
    assert service.is_running
    assert service.is_enabled
```

```python
# test_leap.py #
import pytest
from test_image import *          # Import all generic image tests

@pytest.mark.parametrize("repo,name", [
    ("repo-oss", "openSUSE-Leap-42.1-Oss"),
    ("repo-non-oss", "openSUSE-Leap-42.1-Non-Oss"),
])
def test_repos(CheckRepo, repo, name):
    assert CheckRepo(repo, name)
```

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

**Test invocation**

To invoke the entire test suite for a Leap image in EC2 the test_leap_ec2.py
target would be used.

To invoke a specific test the Pytest conventions can be used:
```
test_leap_ec2.py::test_services_running_enabled.
```

To run only one parameterized test append ids and use [local-ID]:
```
@pytest.mark.parametrize("name", [
    ("cloud-init"),
    ("amazon-ssm-agent"),
], ids=['ci', 'ssm'])


test_leap_ec2.py::test_services_running_enabled[local-ssm]
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

And that's all that's needed. A simple command runs the tests on a remote
instance and returns the results:

```
smarlow@smarlow:~/projects/testinfra> testinfra -v test.py 
--ssh-config=ssh.config --hosts=0.0.0.0
============================= test session starts =============================
platform linux -- Python 3.5.1, pytest-3.0.5, py-1.4.32, pluggy-0.4.0 
-- /usr/bin/python3

cachedir: .cache
rootdir: /home/smarlow/projects/testinfra, inifile: 
plugins: testinfra-1.5.2
collected 7 items 

..test_packages[paramiko://0.0.0.0-python-virtualenv-13] PASSED
..test_echo[paramiko://0.0.0.0] PASSED
..test_repos[paramiko://0.0.0.0-repo-oss-openSUSE-Leap-42.1-Oss] PASSED
..test_services_running_enabled[paramiko://0.0.0.0-cloud-init] PASSED
..test_packages[paramiko://0.0.0.0-python-2.7] PASSED
..test_repos[paramiko://0.0.0.0-repo-non-oss-openSUSE-Leap-42.1-Non-Oss] PASSED
..test_services_running_enabled[paramiko://0.0.0.0-amazon-ssm-agent] PASSED

================= 7 passed, 1 pytest-warnings in 3.64 seconds =================
```

This was run against a Leap instance in EC2. Testinfra could also output a
junit formatted xml file with test results. And likely a json output could
be implemented pretty simply.  With testinfra we don't have to
rewrite a test infrastructure, it provides what we need to build simple
repeatable and extendable tests and it's in python so integration is simple.

**Pytest**

Any other functionality provided by pytest for writing the tests can be used.
See pytest docs for more information. <sup>[[4]](#4)</sup>

**Summary**

Considering all of the notes my suggestion for the testing framework would
be to leverage the testinfra package over other options.

The stack in use would look like:
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

