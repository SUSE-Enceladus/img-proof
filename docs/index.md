---
layout: default
title: Home
navigation_weight: 1
---

# IPA

Image Proofing App

## overview

**IPA** provides a command line utility to test images in the Public
Cloud (AWS, Azure, GCE, etc.).

With **IPA** you can now test custom images in a provider agnostic way
with one tool and one API. In the first release, **IPA** supports the
openSUSE and SLES distributions. It also supports the three largest
cloud providers (AWS, Azure and GCE). However, it is intended to be
distribution agnostic and framework transparent so both are easily
extensible.

For each distribution there are specific synchronization points that
must be provided. These currently include soft reboot and system update.
The synch points not only test functionality but also act as dividers to
separate distinct sections of a test suite. For example you can run a
test to ensure the proper repos exist before and after a system update.
The system update synch point will guarantee the order of tests.
Speaking of tests, if you're already familiar with Pytest conventions
there's no need to learn a whole new unit testing framework. **IPA** is
written in Python and leverages the Pytest framework through Testinfra.

## Installation

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

## Contents

-   [Getting Started](start.md)
-   [Writing Tests](tests.md)
-   [Source Overview](source.md)
