# -*- coding: utf-8 -*-

"""Utility methods for img-proof cli endpoints."""

# Copyright (c) 2019 SUSE LLC. All rights reserved.
#
# This file is part of img-proof. img-proof provides an api and command line
# utilities for testing images in the Public Cloud.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import shlex
import shutil
import sys

import click

from img_proof.ipa_controller import collect_results
from img_proof.ipa_utils import parse_test_name, update_history_log


def archive_history_item(item, destination, no_color):
    """
    Archive the log and results file for the given history item.

    Copy the files and update the results file in destination directory.
    """
    log_src, description = split_history_item(item.strip())

    # Get relative path for log:
    # {provider}/{image}/{instance}/{timestamp}.log
    log_dest = os.path.sep.join(log_src.rsplit(os.path.sep, 4)[1:])

    # Get results src and destination based on log paths.
    results_src = log_src.rsplit('.', 1)[0] + '.results'
    results_dest = log_dest.rsplit('.', 1)[0] + '.results'

    destination_path = os.path.join(destination, log_dest)
    log_dir = os.path.dirname(destination_path)

    try:
        if not os.path.isdir(log_dir):
            os.makedirs(log_dir)

        # Copy results and log files to archive directory.
        shutil.copyfile(log_src, destination_path)
        shutil.copyfile(results_src, os.path.join(destination, results_dest))
    except Exception as error:
        echo_style(
            'Unable to archive history item: %s' % error,
            no_color,
            fg='red'
        )
        sys.exit(1)
    else:
        # Only update the archive results log if no error occur.
        update_history_log(
            os.path.join(destination, '.history'),
            description=description,
            test_log=log_dest
        )


def echo_log(log_file, no_color):
    try:
        with open(log_file, 'r') as f:
            log_output = ''.join(f.readlines())
    except Exception as error:
        echo_style(
            'Unable to open results log file: %s' % error,
            no_color,
            fg='red'
        )
        sys.exit(1)

    click.echo(log_output)


def echo_results(data, no_color, verbose=False):
    """Print test results in nagios style format."""
    try:
        summary = data['summary']
    except KeyError as error:
        click.secho(
            'The results json is missing key: %s' % error,
            fg='red'
        )
        sys.exit(1)

    if 'failed' in summary or 'error' in summary:
        fg = 'red'
        status = 'FAILED'
    else:
        fg = 'green'
        status = 'PASSED'

    results = '{} tests={}|pass={}|skip={}|fail={}|error={}'.format(
        status,
        str(summary.get('num_tests', 0)),
        str(summary.get('passed', 0)),
        str(summary.get('skipped', 0)),
        str(summary.get('failed', 0)),
        str(summary.get('error', 0))
    )
    echo_style(results, no_color, fg=fg)

    if verbose:
        echo_verbose_results(data, no_color)


def echo_results_file(results_file, no_color, verbose=False):
    """Print test results in nagios style format."""
    try:
        data = collect_results(results_file)
    except ValueError:
        echo_style(
            'The results file is not the proper json format.',
            no_color,
            fg='red'
        )
        sys.exit(1)
    except Exception as error:
        echo_style(
            'Unable to process results file: %s' % error,
            no_color,
            fg='red'
        )
        sys.exit(1)

    echo_results(data, no_color, verbose)


def echo_style(message, no_color, fg='yellow'):
    if no_color:
        click.echo(message)
    else:
        click.secho(message, fg=fg)


def echo_verbose_results(data, no_color):
    """Print list of tests and result of each test."""
    click.echo()
    click.echo(
        '\n'.join(
            '{}: {}'.format(key, val) for key, val in data['info'].items()
        )
    )
    click.echo()
    for test in data['tests']:
        if test['outcome'] == 'passed':
            fg = 'green'
        elif test['outcome'] == 'skipped':
            fg = 'yellow'
        else:
            fg = 'red'

        name = parse_test_name(test['name'])
        echo_style(
            '{} {}'.format(name, test['outcome'].upper()),
            no_color,
            fg=fg
        )


def get_log_file_from_item(history):
    """
    Return the log file based on provided history item.

    Description is optional.
    """
    try:
        log_file, description = shlex.split(history)
    except ValueError:
        log_file = history.strip()

    return log_file


def results_history(history_log, no_color):
    """Display a list of img_proof test results history."""
    try:
        with open(history_log, 'r') as f:
            lines = f.readlines()
    except Exception as error:
        echo_style(
            'Unable to process results history log: %s' % error,
            no_color,
            fg='red'
        )
        sys.exit(1)

    index = len(lines)
    for item in lines:
        click.echo('{} {}'.format(index, item), nl=False)
        index -= 1


def split_history_item(history):
    """
    Return the log file and optional description for item.
    """
    try:
        log_file, description = shlex.split(history)
    except ValueError:
        log_file = history.strip()
        description = None

    return log_file, description
