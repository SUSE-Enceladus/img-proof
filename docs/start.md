---
layout: default
title: Overview
navigation_weight: 2
---

Requirements
============

- apache-libcloud
- azure-common
- azure-mgmt-compute
- azure-mgmt-network
- azure-mgmt-resource
- certifi
- Click
- cryptography
- paramiko
- pycryptodome
- pytest
- PyYaml
- testinfra

Installation
============

To install the openSUSE package use the following commands as root:

```shell
$ zypper ar http://download.opensuse.org/repositories/Cloud:/Tools/<distribution>
$ zypper refresh
$ zypper in python3-ipa
```
   
From PyPI:

```shell
$ pip install python3-ipa
```

Or you can install the latest development version from github:

```shell
# latest source
$ pip install git+https://github.com/SUSE-Enceladus/ipa.git

# specific branch or release
$ pip install git+https://github.com/SUSE-Enceladus/ipa.git@{branch/release}
```

See [PyPi
docs](https://pip.pypa.io/en/stable/reference/pip_install/#vcs-support)
for more information on vcs support.

Configuration
=============

The framework configuration file is ini format \~/.config/ipa/config.
Anything specific to the test framework can be found in this file. Thus
anything that is cloud framework independent such as the tests dir and
results dir.

To override the default configuration location the CLI option `-C` or
`--config` is provided.

The following is an example configuration file. The ipa section is
required and the provider sections are optional and can be \[ec2\],
\[gce\], \[azure\] or \[ssh\].

```ini
[ipa]
tests=~/ipa/tests/
results=~/ipa/results/

[ec2]
region=us-west-1
```

Azure
-----

Azure uses service principals for authentication. See [Azure
docs](https://docs.microsoft.com/en-us/python/azure/python-sdk-azure-authenticate?view=azure-python#mgmt-auth-file)
for more info on creating a service principal json file. Additional
configuration options can be placed in the `azure` section of the `ipa`
configuration file.

EC2
---

For testing EC2 instances **ipa** will use the ec2utils configuration
file located at \~/.ec2utils.conf. See
[ec2utils](https://github.com/SUSE-Enceladus/Enceladus/tree/master/ec2utils) for
an example configuration file.

GCE
---

GCE uses service accounts for authentication. The service account is
required to have the following:

- Compute Instance Admin (v1) Role
  ([roles/compute.instanceAdmin.v1](https://cloud.google.com/compute/docs/access/iam))
- Service Account User Role
  ([roles/iam.serviceAccountUser](https://cloud.google.com/compute/docs/access/iam))
- Private key (JSON format)
    - Save this file in a secure location as it cannot be recovered.

The path to the JSON private key can be added to IPA configuration:

**example.ipa.config.**

```ini
[ipa]

[gce]
service_account_file = /path/to/service-account.json
```

> Additional configuration options can be placed in the `gce` section of
> the `ipa` configuration file.

To create a service account and generate the proper JSON file follow the
[Libcloud
docs](http://libcloud.readthedocs.io/en/latest/compute/drivers/gce.html#service-account)
or [Google
docs](https://cloud.google.com/iam/docs/creating-managing-service-accounts).

For more information on updating an existing service account:

- Create a new JSON private key:
  [creating-managing-service-account-keys](https://cloud.google.com/iam/docs/creating-managing-service-account-keys)
- Granting roles:
  [granting-roles-to-service-accounts](https://cloud.google.com/iam/docs/granting-roles-to-service-accounts)

SSH
---
Requires no provider credentials to test instances. SSH user, SSH private key can
be placed in ssh section of config. The instance to be tested must be running.

Provider Configuration location
-------------------------------

To override the provider configuration the CLI option,
`--provider-config` is available.

Usage
=====

CLI
---

```shell
$ ipa test
```

Test image in the given framework using the supplied test files.

#### Testing an image in EC2

```shell
$ ipa test -i {image-id} \
  -a {account} \
  --provider-config ~/.ec2utils.conf \
  --no-cleanup \
  -d openSUSE_Leap \
  ec2 test_image

Starting instance
Running tests /home/{user}/ipa/tests/test_image.py
PASSED tests=1|pass=1|fail=0|error=0
```

#### Testing an image in Azure

```shell
$ ipa test -i {image-id} \
  --no-cleanup \
  -d openSUSE_Leap \
  --ssh-private-key {azure-ssh-key-file} \
  azure test_image

Starting instance
Running tests /home/{user}/ipa/tests/test_image.py
PASSED tests=1|pass=1|fail=0|error=0
```

#### Testing an image in GCE

```shell
$ ipa test -i {image-id} \
  --no-cleanup \
  -d openSUSE_Leap \
  gce test_image

Starting instance
Running tests /home/{user}/ipa/tests/test_image.py
PASSED tests=1|pass=1|fail=0|error=0
```

#### Testing an image in SSH

```shell
$ ipa test -ip-address 10.0.0.1 \
  -d openSUSE_Leap \
  ssh test_image

Running tests /home/{user}/ipa/tests/test_image.py
PASSED tests=1|pass=1|fail=0|error=0
```

### Verbosity

The CLI output verbosity can be controlled via options:

`--debug`

Display debug level logging to console.

`--verbose`

(Default) Display logging info to console.

`--quiet`

Silence logging information on test run.

### Cleanup

By default the instance will be terminated if all tests pass. If a test
fails the instance will remain running. This behavior can be changed
with the `--cleanup` and `--no-cleanup` flags.

`--cleanup`

Instance will be terminated in all cases.

`--no-cleanup`

Instance will remain running in all cases.

### ANSI Style

By default the command line output will be colored. To disable color
output use the `--no-color` option.

### Early Exit

The early exit option will stop the test run on the first failure.
`--early-exit` is passed to Pytest as `-x`. See [Pytest
docs](https://docs.pytest.org/en/latest/usage.html#stopping-after-the-first-or-n-failures)
for more info.

### Requirements and external test injection

Using the `--inject` option; packages, archives and files can be
injected on the test instance. This also provides the ability to install
packages in an existing repository and run commands on the test
instance. The following sections may be provided in a YAML style config
file. Each section can be a single item or a list of items. All files
are copied and extracted to the default SSH location for the test
instance. This is generally the user's home directory.

***inject\_packages***

an rpm path or list of rpm paths which will be copied and installed
on the test instance.

***inject\_archives***

an archive or list of archives which will be copied and extracted on
the test instance.

***inject\_files***

a file path or list of file paths which will be copied to the test
instance.

***execute***

a command or list of commands to run on the test instance.

***install***

a package name or list of package names to install from an existing
repo on the test instance.

The order of processing for the sections is as follows:

1.  inject\_packages
2.  inject\_archives
3.  inject\_files
4.  execute
5.  install

#### Example

**testing\_injection.yaml.**

```yaml
inject_packages: /home/user/test.noarch.rpm
inject_archives: /home/user/test.tar.xz
inject_files: /home/user/test.py
install:
  - python3
  - python3-Django
execute: python test.py
```

```shell
$ ipa test ... --inject testing_injection.yaml
```

Code
----

**ipa** primarily provides a CLI tool for testing images. However, the
endpoints can be imported directly in Python 3 code through the
controller.

```python
from ipa.ipa_controller import test_image

status, results = test_image(
    provider,
    access_key_id,
    ...
    storage_container,
    tests
)
```
