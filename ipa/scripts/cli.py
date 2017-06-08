#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Ipa CLI endpoints using click library."""

# Copyright (c) 2017 SUSE LLC
#
# This file is part of ipa.
#
# See LICENSE for license information.

import sys

import click

from ipa.ipa_constants import SUPPORTED_DISTROS, SUPPORTED_PROVIDERS
from ipa.ipa_controller import test_image
from ipa.scripts.cli_constants import (
    HELP_ACCESS_KEY_ID,
    HELP_ACCOUNT,
    HELP_CLEANUP,
    HELP_CONFIG,
    HELP_DISTRO,
    HELP_IMAGE_ID,
    HELP_REGION,
    HELP_RUNNING_INSTANCE,
    HELP_SECRET_ACCESS_KEY,
    HELP_SSH_PRIVATE_KEY,
    HELP_SSH_USER,
    HELP_STORAGE_CONTAINER,
    HELP_TERMINATE,
    HELP_TYPE,
)


@click.group()
@click.version_option()
def main():
    """
    Ipa provides a Python API and command line utility for testing images.

    It can be used to test images in the Public Cloud (AWS, Azure, GCE, etc.).
    """
    pass


@click.command()
@click.argument(
    'provider',
    type=click.Choice(SUPPORTED_PROVIDERS)
)
@click.option(
    '-A',
    '--access-key-id',
    help=HELP_ACCESS_KEY_ID
)
@click.option(
    '-a',
    '--account',
    help=HELP_ACCOUNT
)
@click.option(
    '--cleanup/--no-cleanup',
    default=None,
    help=HELP_CLEANUP
)
@click.option(
    '-C',
    '--config',
    type=click.Path(exists=True),
    help=HELP_CONFIG
)
@click.option(
    '-d',
    '--distro',
    type=click.Choice(SUPPORTED_DISTROS),
    help=HELP_DISTRO
)
@click.option(
    '-i',
    '--image-id',
    help=HELP_IMAGE_ID
)
@click.option(
    '-t',
    '--instance-type',
    help=HELP_TYPE
)
@click.option(
    '-r',
    '--region',
    help=HELP_REGION
)
@click.option(
    '-R',
    '--running-instance',
    help=HELP_RUNNING_INSTANCE
)
@click.option(
    '-s',
    '--secret-access-key',
    help=HELP_SECRET_ACCESS_KEY
)
@click.option(
    '-p',
    '--ssh-private-key',
    type=click.Path(exists=True),
    help=HELP_SSH_PRIVATE_KEY
)
@click.option(
    '-u',
    '--ssh-user',
    help=HELP_SSH_USER
)
@click.option(
    '-S',
    '--storage-container',
    help=HELP_STORAGE_CONTAINER
)
@click.option(
    '--terminate',
    is_flag=True,
    help=HELP_TERMINATE
)
@click.argument('tests', nargs=-1)
def test(provider,
         access_key_id,
         account,
         cleanup,
         config,
         distro,
         image_id,
         instance_type,
         region,
         running_instance,
         secret_access_key,
         ssh_private_key,
         ssh_user,
         storage_container,
         terminate,
         tests):
    """Test image in the given cloud framework using the supplied test file."""
    click.secho('Testing image...', fg='green')
    try:
        status, results = test_image(
            provider,
            access_key_id,
            account,
            cleanup,
            config,
            distro,
            image_id,
            instance_type,
            region,
            running_instance,
            secret_access_key,
            ssh_private_key,
            ssh_user,
            storage_container,
            terminate,
            tests
        )
        # TODO: Print results
        sys.exit(status)
    except Exception as e:
        click.secho(
            "{}: {}".format(type(e).__name__, e),
            fg='red'
        )
        sys.exit(1)


@click.command()
def results():
    """
    Print test results info from provided results json file.

    If verbose option selected, print all test cases,
    otherwise print number of tests/successes/failures/errors.
    """
    try:
        raise Exception('Results command not implemented :( ... yet.')
    except Exception as e:
        click.echo(click.style("Broken: %s" % e, fg='red'))
        sys.exit(1)


@click.command(name='list')
def list_tests():
    """
    Print a list of test files or test cases.

    If verbose option selected, print all tests cases in
    each test file, otherwise print the test files only.
    """
    try:
        raise Exception('List tests command not implemented :( ... yet.')
    except Exception as e:
        click.echo(click.style("Broken: %s" % e, fg='red'))
        sys.exit(1)


main.add_command(test)
main.add_command(results)
main.add_command(list_tests)

if __name__ == "__main__":
    main()
