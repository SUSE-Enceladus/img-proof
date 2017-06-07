#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Ipa CLI endpoints using click library."""
#
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
    HELP_DISTRO,
    HELP_RUNNING_INSTANCE,
    HELP_SSH_PRIVATE_KEY,
    HELP_SSH_USER,
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
    '-d',
    '--distro',
    type=click.Choice(SUPPORTED_DISTROS),
    help=HELP_DISTRO
)
@click.option(
    '-R',
    '--running-instance',
    help=HELP_RUNNING_INSTANCE
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
def test(provider,
         distro,
         running_instance,
         ssh_private_key,
         ssh_user):
    """Test image in the given cloud framework using the supplied test file."""
    click.secho('Testing image...', fg='green')
    try:
        status, results = test_image(
            provider,
            distro,
            running_instance,
            ssh_private_key,
            ssh_user,
        )
        # TODO: print results
        sys.exit(status)
    except Exception as e:
        click.secho(
            "{}: {}".format(type(e).__name__, e),
            fg='red'
        )
        sys.exit(1)


@click.command()
def results():
    try:
        raise Exception('Results command not implemented :( ... yet.')
    except Exception as e:
        click.echo(click.style("Broken: %s" % e, fg='red'))
        sys.exit(1)


@click.command(name='list')
def list_tests():
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
