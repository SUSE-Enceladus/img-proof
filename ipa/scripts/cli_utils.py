# -*- coding: utf-8 -*-

"""Utility methods for ipa cli endpoints."""

# Copyright (c) 2017 SUSE LLC
#
# This file is part of ipa. Ipa provides an api and command line
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
import sys

import click


def echo_results(data):
    """Print test results in nagios style format."""
    if 'failed' in data or 'error' in data:
        fg = 'red'
        status = 'FAILED'
    else:
        fg = 'green'
        status = 'PASSED'

    results = '{} tests={}|pass={}|fail={}|error={}'.format(
        status,
        str(data.get('num_tests', 0)),
        str(data.get('passed', 0)),
        str(data.get('failed', 0)),
        str(data.get('error', 0))
    )
    click.secho(results, bold=True, fg=fg)


def echo_verbose_results(data, name_color='yellow'):
    """Print list of tests and result of each test."""
    echo_results(data['summary'])
    click.echo()
    click.secho(
        '\n'.join(
            '{}: {}'.format(key, val) for key, val in data['info'].items()
        )
    )
    click.echo()
    for test in data['tests']:
        if test['outcome'] == 'passed':
            fg = 'green'
        else:
            fg = 'red'

        name = test['name'].split(os.sep)[-1].replace('.py', '')
        click.secho(
            '{} {}'.format(name, test['outcome'].upper()),
            bold=True,
            fg=fg
        )


def results_history(history_log):
    """Display a list of ipa test results history."""
    try:
        with open(history_log, 'r') as f:
            history_file = ''.join(f.readlines())
        click.echo(history_file)
    except Exception as error:
        click.secho(
            'Unable to process results history log.',
            fg='red'
        )
        sys.exit(1)
