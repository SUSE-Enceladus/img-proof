Installation
============

```shell
$ git clone https://github.com/SUSE/ipa.git
$ cd ipa

# Activate virtual Environment then install
# ipa and dev dependences in editable mode
$ pip install -e .[dev]
```

ipa is now installed in the active virtual environment in development
mode.

Dev Requirements
================

- bumpversion
- pip\>=7.0.0

Testing Requirements
====================

- coverage
- flake8
- mock
- pytest-cov

Contribution Checklist
======================

- All patches must be signed. [Signing Commits](#signing-commits)
- All contributed code must conform to flake8. [Code Style](#code-style)
- All new code contributions must be accompanied by a test.
    - Tests must pass and coverage remain above 90%. [Unit & Integration Tests](#unit-&-integration-tests)
- Follow Semantic Versioning. [Versions & Releases](#versions-&-releases)

Versions & Releases
===================

**ipa** adheres to Semantic versioning; see <http://semver.org/> for
details.

[bumpversion](https://pypi.python.org/pypi/bumpversion/) is used for
release version management, and is configured in `setup.cfg`:

```shell
$ bumpversion major|minor|patch
$ git push
```

Bumpversion will create a commit with version updated in all locations.
The annotated tag is created separately.

```shell
$ git tag -a v{version}
# git tag -a v0.0.1

# Create a message with the changes since last release and push tags.
$ git push --tags
```

Unit & Integration Tests
========================

All tests should pass and test coverage should remain above 90%.

The tests and coverage can be run directly via pytest.

```shell
$ pytest --cov=ipa
```

Testing with tox
================

Requirements
------------

- tox
- tox-pyenv (testing multiple Python versions 3.4+)

Setup
-----

- Install tox
    
    ```shell
    $ pip install .\[tox\]
    ```

- Setup pyenv

    See the [pyenv doc](https://github.com/pyenv/pyenv#installation) for
    more info.

- Run tox

    ```shell
    $ tox (test all versions 3.4+)

    # or
    $ tox -e py{version}
    $ tox -e py36
    ```

Code Style
==========

Source should pass flake8 and pep8 standards.

```shell
$ flake8 ipa
```

Man Pages
=========

If the CLI is changed the man pages can be auto-generated.

-   Install click-man
    
    ```shell
    $ pip install click-man
    ```

-   Generate man pages

    ```shell
    $ python3 setup.py \
      --command-packages=click_man.commands man_pages \
      --target man/man1
    ```

Signing Commits
===============

The repository and the code base patches sent for inclusion must be GPG
signed. See the GitHub article, [Signing commits using
GPG](https://help.github.com/articles/signing-commits-using-gpg/), for
more information.
