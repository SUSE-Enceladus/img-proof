![Continuous testing & Linting](https://github.com/SUSE-Enceladus/img-proof/workflows/Continuous%20testing%20&%20Linting/badge.svg)
[![Documentation Status](https://readthedocs.org/projects/img-proof/badge/?version=latest)](https://img-proof.readthedocs.io/en/latest/?badge=latest)
[![Py Versions](https://img.shields.io/pypi/pyversions/img-proof.svg)](https://pypi.org/project/img-proof/)
[![License](https://img.shields.io/pypi/l/img-proof.svg)](https://pypi.org/project/img-proof/)

[![img-proof](https://raw.githubusercontent.com/SUSE-Enceladus/img-proof/master/docs/source/_images/logo.png "img-proof Logo")](https://github.com/SUSE-Enceladus/img-proof)

overview
========

**img-proof** (IPA) provides a command line utility to test
images in the Public Cloud (AWS, Azure, GCE, etc.).

With **img-proof** you can now test custom images in a cloud framework agnostic way
with one tool and one API. In the first release, **img-proof** supports the
openSUSE and SLES distributions. It also supports the three largest
cloud frameworks (AWS, Azure and GCE). However, it is intended to be
distribution agnostic and framework transparent so both are easily
extensible.

For each distribution there are specific synchronization points that
must be provided. These currently include soft reboot and system update.
The synch points not only test functionality but also act as dividers to
separate distinct sections of a test suite. For example you can run a
test to ensure the proper repos exist before and after a system update.
The system update synch point will guarantee the order of tests.
Speaking of tests, if you're already familiar with Pytest conventions
there's no need to learn a whole new unit testing framework. **img-proof** is
written in Python and leverages the Pytest framework through Testinfra.

Installation
============

To install the package use the following commands as root:

```shell
$ zypper ar http://download.opensuse.org/repositories/Cloud:/Tools/<distribution>
$ zypper refresh
$ zypper in python3-img-proof
```

Requirements
============

-   boto3
-   apache-libcloud
-   azure-common
-   azure-mgmt-compute
-   azure-mgmt-network
-   azure-mgmt-resource
-   Click
-   paramiko
-   pytest
-   PyYaml
-   testinfra
-   oci

# [Docs](https://img-proof.readthedocs.io/en/latest/)

Tests
=====

**img-proof** uses the Testinfra package for writing unit tests. Testinfra
leverages Pytest and provides modules such as Package, Process and
Service to test the state of images. See the [Testinfra
Docs](https://testinfra.readthedocs.io/en/latest/) for more information
on writing infrastructure tests.

> **img-proof** currently passes the Pytest option `-x` (stop on first
> failure) through as `--early-exit`. If there's an interest or need for
> any other options/args please submit an issue to
> [Github](https://github.com/SUSE-Enceladus/img-proof/issues).

CLI Overview
============

The CLI provides multiple subcommands to initiate image testing:

* `img-proof test`

   Test image in the given framework using the supplied test files.

* `img-proof results`

   Invokes the default show subcommand `img-proof results show 1`.

* `img-proof results clear`

   Clear the results from the history file.

* `img-proof results delete`

   Delete the specified history item from the history log.

* img-proof results list`

   Display list of results history.

* `img-proof results show`

   Display the results or log file for a history item.

* `img-proof list`

   Print a list of test files or test cases.

Issues/Enhancements
===================

Please submit issues and requests to
[Github](https://github.com/SUSE-Enceladus/img-proof/issues).

Contributing
============

Contributions to **ipa** are welcome and encouraged. See
[CONTRIBUTING](https://github.com/SUSE-Enceladus/img-proof/blob/master/CONTRIBUTING.md)
for info on getting started.

License
=======

Copyright (c) 2018 SUSE LLC.

Distributed under the terms of GPL-3.0+ license, see
[LICENSE](https://github.com/SUSE-Enceladus/img-proof/blob/master/LICENSE)
for details.
