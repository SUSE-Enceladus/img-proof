#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""Ipa CLI unit tests."""

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

from ipa.scripts.cli import main

from click.testing import CliRunner

import pytest


def test_cli_ipa_help():
    """Confirm ipa --help is successful."""
    runner = CliRunner()
    result = runner.invoke(main, ['--help'])
    assert result.exit_code == 0
    assert 'Ipa provides a Python API and command line utility' \
           ' for testing images.' in result.output


@pytest.mark.parametrize(
    "endpoint,value",
    [('list',
      'Print a list of test files or test cases.'),
     ('results',
      'Process provided history log and results files.'),
     ('test',
      'Test image in the given framework using the supplied test files.')],
    ids=['ipa-list', 'ipa-results', 'ipa-test']
)
def test_cli_help(endpoint, value):
    """Confirm ipa list --help is successful."""
    runner = CliRunner()
    result = runner.invoke(main, [endpoint, '--help'])
    assert result.exit_code == 0
    assert value in result.output


def test_cli_provider_missing():
    """Confirm error if provider not supplied for test endpoint."""
    runner = CliRunner()
    result = runner.invoke(main, ['test'])
    assert result.exit_code != 0
    assert 'Error: Missing argument "provider"' in result.output


def test_cli_invalid_provider():
    """Confirm error if invalid provider supplied."""
    runner = CliRunner()
    result = runner.invoke(main, ['test', 'Provider'])
    assert result.exit_code != 0
    assert 'Error: Invalid value for "provider"' in result.output


def test_cli_invalid_distro():
    """Confirm error if invalid distro provided."""
    runner = CliRunner()
    result = runner.invoke(main, ['test', '-d', 'Distro'])
    assert result.exit_code != 0
    assert 'Error: Invalid value for "-d" / "--distro"' in result.output


def test_cli_test_image_exception():
    """Confirm exception if missing image id and running instance."""
    runner = CliRunner()
    result = runner.invoke(
        main,
        ['test', 'ec2', '-d', 'SLES', '-C', 'tests/data/config']
    )
    assert result.exit_code != 0
    assert 'Image ID or running instance is required.' in result.output


def test_cli_list():
    """Test ipa list endpoint."""
    runner = CliRunner()
    result = runner.invoke(main, ['list', 'tests/data/tests'])
    assert result.exit_code == 0


def test_cli_list_verbose():
    """Test ipa list endpoint."""
    runner = CliRunner()
    result = runner.invoke(main, ['list', '-v', 'tests/data/tests'])
    assert result.exit_code == 0


def test_cli_results():
    """Test ipa results endpoint."""
    runner = CliRunner()
    result = runner.invoke(
        main,
        ['results',
         '--history-log',
         'tests/data/.history',
         'show', '-v', '-r',
         'tests/data/test.results']
    )
    assert result.exit_code == 0


def test_cli_results_log():
    """Test ipa results log display."""
    runner = CliRunner()
    result = runner.invoke(
        main,
        ['results',
         '--history-log',
         'tests/data/.history',
         'show', '-l', '-r',
         'tests/data/history.log']
    )
    assert result.exit_code == 0


def test_cli_results_show_exception():
    """Test ipa results show handles exception."""
    runner = CliRunner()
    result = runner.invoke(
        main,
        ['results', '--history-log', 'tests/data/.history', 'show', '100']
    )
    assert result.exit_code != 0
    assert 'History result at index 100 does not exist.' in result.output


def test_cli_results_history():
    """Test ipa results history."""
    runner = CliRunner()
    result = runner.invoke(
        main,
        ['results', '--history-log', 'tests/data/.history', 'list']
    )
    assert result.exit_code == 0


def test_cli_results_history_exception():
    """Test ipa results history handles exception if file missing."""
    runner = CliRunner()
    result = runner.invoke(
        main,
        ['results', '--history-log', 'tests/data/.history', 'show', '0']
    )
    assert result.exit_code != 0
    assert 'Unable to process results file:' in result.output


def test_cli_results_history_log_exception():
    """Test ipa results history handles exception if key missing."""
    runner = CliRunner()
    result = runner.invoke(
        main,
        ['results',
         '--history-log',
         'tests/data/.history',
         'show', '-l', '0']
    )
    assert result.exit_code != 0
    assert 'Unable to open results log file' in result.output


def test_cli_results_history_log():
    """Test ipa results history."""
    runner = CliRunner()
    result = runner.invoke(
        main,
        ['results', '--history-log', 'tests/data/.history', 'show', '-l']
    )
    assert result.exit_code == 0


def test_cli_history():
    """Test ipa list history sub command."""
    runner = CliRunner()
    result = runner.invoke(
        main,
        ['results', '--history-log', 'tests/data/.history', 'list']
    )
    assert result.exit_code == 0


def test_cli_clear_history():
    """Test ipa clear history sub command."""
    lines = ''
    with open('tests/data/.history') as history_log:
        lines = history_log.readlines()

    runner = CliRunner()
    with runner.isolated_filesystem():
        try:
            os.makedirs('test')
        except OSError as error:
            pass

        with open('test/.history', 'w') as history_log:
            history_log.writelines(lines)

        result = runner.invoke(
            main,
            ['results', '--history-log', 'test/.history', 'clear']
        )
        assert result.exit_code == 0

        result = runner.invoke(
            main,
            ['results', '--history-log', 'test/.history', 'list']
        )
        assert 'Path "test/.history" does not exist.' in result.output


def test_cli_delete_history_item():
    """Test ipa delete history item at given index."""
    lines = []
    with open('tests/data/.history') as history_log:
        lines = history_log.readlines()

    before_count = len(lines)
    runner = CliRunner()
    with runner.isolated_filesystem():
        try:
            os.makedirs('test')
        except OSError as error:
            pass

        with open('test/.history', 'w') as history_log:
            history_log.writelines(lines)

        result = runner.invoke(
            main,
            ['results', '--history-log', 'test/.history', 'delete', '1']
        )
        assert result.exit_code == 0

        with open('test/.history') as history_log:
            lines = history_log.readlines()
        assert before_count - 1 == len(lines)


def test_cli_history_empty():
    """Test ipa history endpoint with empty history log."""
    runner = CliRunner()
    result = runner.invoke(
        main,
        ['results', '--history-log', 'tests/data/empty.history', 'list']
    )
    assert result.exit_code == 0


def test_cli_results_non_json():
    """Test ipa results non json file provided."""
    runner = CliRunner()
    result = runner.invoke(
        main,
        ['results',
         '--history-log',
         'tests/data/.history',
         'show', '-v', '-r',
         'tests/data/config']
    )
    assert result.exit_code == 1
    assert result.output.strip() == \
        'The results file is not the proper json format.'


def test_cli_results_missing_key():
    """Test ipa results json file missing key."""
    runner = CliRunner()
    result = runner.invoke(
        main,
        ['results',
         '--history-log',
         'tests/data/.history',
         'show', '-v', '-r',
         'tests/data/bad.results']
    )
    assert result.exit_code == 1
    assert result.output.strip() == \
        "The results json is missing key: 'summary'"


def test_cli_license():
    """Test ipa cli license."""
    runner = CliRunner()
    result = runner.invoke(
        main,
        ['--license']
    )
    assert result.exit_code == 0
    assert result.output.strip() == 'GPLv3+'
