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


@click.group()
@click.version_option()
def main():
    """
    Ipa provides a Python API and command line utility for testing images.

    It can be used to test images in the Public Cloud (AWS, Azure, GCE, etc.).
    """
    pass


@click.command()
@click.option(
    '--access-key-id',
    help='EC2 access key ID for login credentials.'
)
@click.option(
    '-a',
    '--account',
    help='Settings account to provide connection information.'
)
@click.option(
    '--cleanup/--no-cleanup',
    default=None,
    help='Terminate instance after tests. By default an instance will be '
         'deleted on success and left running if there is a test failure.'
)
@click.option(
    '-C',
    '--config',
    type=click.Path(exists=True),
    help='ipa config file location.'
)
@click.option(
    '-d',
    '--distro',
    type=click.Choice(SUPPORTED_DISTROS),
    help='The distribution of the image.'
)
@click.option(
    '-i',
    '--image-id',
    help='The ID of the image used for instance.'
)
@click.option(
    '-t',
    '--instance-type',
    help='Instance type to use for launching machine.'
)
@click.option(
    '-r',
    '--region',
    help='Cloud provider region to test image.'
)
@click.option(
    '-R',
    '--running-instance',
    help='Running instance ID/Name.'
)
@click.option(
    '--secret-access-key',
    help='EC2 secret access key for login credentials.'
)
@click.option(
    '--ssh-private-key',
    type=click.Path(exists=True),
    help='SSH private key file for accessing instance.'
)
@click.option(
    '-u',
    '--ssh-user',
    help='SSH user for accessing instance.'
)
@click.option(
    '-S',
    '--storage-container',
    help='Azure storage container to use.'
)
@click.option(
    '--terminate',
    is_flag=True,
    help='Terminate test suite on first failure.'
)
@click.argument(
    'provider',
    type=click.Choice(SUPPORTED_PROVIDERS)
)
@click.argument('tests', nargs=-1)
def test(access_key_id,
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
         provider,
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
