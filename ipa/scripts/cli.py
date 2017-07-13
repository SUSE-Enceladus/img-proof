#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Ipa CLI endpoints using click library."""

# Copyright (c) 2017 SUSE LLC
#
# This file is part of ipa.
#
# See LICENSE for license information.

import logging
import pickle
import sys

import click

from ipa.ipa_constants import (
    IPA_HISTORY_FILE,
    SUPPORTED_DISTROS,
    SUPPORTED_PROVIDERS
)
from ipa import ipa_utils
from ipa.ipa_controller import collect_results, test_image
from ipa.scripts.cli_utils import (
    echo_results,
    echo_verbose_results,
    results_history
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
    help='ipa config file location. Default: ~/.config/ipa/config'
)
@click.option(
    '-d',
    '--distro',
    type=click.Choice(SUPPORTED_DISTROS),
    help='The distribution of the image.'
)
@click.option(
    '--early-exit',
    is_flag=True,
    help='Terminate test suite on first failure.'
)
@click.option(
    '-h',
    '--history-log',
    type=click.Path(exists=True),
    help='ipa history log file location. Default: ~/.config/ipa/.history'
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
    '--debug',
    'log_level',
    flag_value=logging.DEBUG,
    help='Display debug level logging to console.'
)
@click.option(
    '--verbose',
    'log_level',
    flag_value=logging.INFO,
    default=True,
    help='(Default) Display logging info to console.'
)
@click.option(
    '--quiet',
    'log_level',
    flag_value=logging.WARNING,
    help='Silence logging information on test run.'
)
@click.option(
    '--provider-config',
    help='The provider specific config file location.'
)
@click.option(
    '-r',
    '--region',
    help='Cloud provider region to test image.'
)
@click.option(
    '--results-dir',
    help='Directory to store test results and output.'
)
@click.option(
    '-R',
    '--running-instance-id',
    help='The ID or Name of running instance to test.'
)
@click.option(
    '--secret-access-key',
    help='EC2 secret access key for login credentials.'
)
@click.option(
    '--ssh-key-name',
    help='SSH private key file name for EC2.'
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
         early_exit,
         history_log,
         image_id,
         instance_type,
         log_level,
         provider_config,
         region,
         results_dir,
         running_instance_id,
         secret_access_key,
         ssh_key_name,
         ssh_private_key,
         ssh_user,
         storage_container,
         provider,
         tests):
    """Test image in the given framework using the supplied test files."""
    try:
        status, results = test_image(
            provider,
            access_key_id,
            account,
            cleanup,
            config,
            distro,
            early_exit,
            history_log,
            image_id,
            instance_type,
            log_level,
            provider_config,
            region,
            results_dir,
            running_instance_id,
            secret_access_key,
            ssh_key_name,
            ssh_private_key,
            ssh_user,
            storage_container,
            tests
        )
        echo_results(results)
        sys.exit(status)
    except Exception as error:
        if log_level == logging.DEBUG:
            raise

        click.secho(
            "{}: {}".format(type(error).__name__, error),
            fg='red'
        )
        sys.exit(1)


@click.command()
@click.option(
    '--clear',
    is_flag=True,
    help='Clear list of results history.'
)
@click.option(
    '--history-log',
    default=IPA_HISTORY_FILE,
    type=click.Path(exists=True),
    help='Location of the history log file to display results from.'
)
@click.option(
    '--list',
    'list_results',
    is_flag=True,
    help='Display list of results history.'
)
@click.option(
    '-l',
    '--log',
    is_flag=True,
    help='Display the log for the given test run.'
)
@click.option(
    '-n',
    '--result',
    default=-1,
    help='Test result item to display.'
)
@click.option(
    '-r',
    '--results-file',
    type=click.Path(exists=True),
    help='The results file or log to parse.'
)
@click.option(
    '-v',
    '--verbose',
    is_flag=True
)
def results(clear,
            history_log,
            list_results,
            log,
            result,
            results_file,
            verbose):
    """
    Print test results info from provided results json file.

    If no results file is supplied display results from most recent
    test in history if it exists.

    If verbose option selected, print all test cases,
    otherwise print number of tests/successes/failures/errors.

    If log option selected display test log in a pager.

    If list option is provided display the results history from
    given history log.

    If the clear option is provided the history will
    be cleared.
    """
    if clear:
        ipa_utils.update_history_log(history_log, clear=True)
    elif list_results:
        results_history(history_log)
    else:
        if not results_file:
            try:
                with open(history_log, 'r+b') as f:
                    data = pickle.load(f)

                if log:
                    results_file = data[result]['log']
                else:
                    results_file = data[result]['results']
            except Exception as error:
                click.secho(
                    'Unable to retrieve results history, '
                    'provide results file or re-run test.',
                    fg='red'
                )
                sys.exit(1)

        if log:
            try:
                with open(results_file, 'r') as f:
                    log_file = ''.join(f.readlines())
                click.echo(log_file)
            except Exception as error:
                click.secho(
                    'Unable to open results log file: %s' % error,
                    fg='red'
                )
                sys.exit(1)
        else:
            try:
                data = collect_results(results_file)

                if verbose:
                    echo_verbose_results(data)
                else:
                    echo_results(data['summary'])
            except ValueError:
                click.secho(
                    'The results file is not the proper json format.',
                    fg='red'
                )
                sys.exit(1)
            except KeyError as error:
                click.secho(
                    'The results json is missing key: %s' % error,
                    fg='red'
                )
                sys.exit(1)
            except Exception as error:
                click.secho(
                    'Unable to process results file: %s' % error,
                    fg='red'
                )
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
