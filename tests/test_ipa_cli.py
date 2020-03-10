#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""img_proof CLI unit tests."""

# Copyright (c) 2019 SUSE LLC. All rights reserved.
#
# This file is part of img_proof. img_proof provides an api and command line
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

from img_proof.scripts.cli import main

from click.testing import CliRunner

import pytest


def test_cli_ipa_help():
    """Confirm img_proof --help is successful."""
    runner = CliRunner()
    result = runner.invoke(main, ['--help'])
    assert result.exit_code == 0
    assert 'img-proof provides a Python API and cmd line utility' \
           ' for testing images.' in result.output


@pytest.mark.parametrize(
    "endpoint,value",
    [('list',
      'Print a list of test files or test cases.'),
     ('results',
      'Process provided history log and results files.'),
     ('test',
      'Test image in the given framework using the supplied test files.')],
    ids=['img_proof-list', 'img_proof-results', 'img_proof-test']
)
def test_cli_help(endpoint, value):
    """Confirm img_proof list --help is successful."""
    runner = CliRunner()
    result = runner.invoke(main, [endpoint, '--help'])
    assert result.exit_code == 0
    assert value in result.output


def test_cli_provider_missing():
    """Confirm error if provider not supplied for test endpoint."""
    runner = CliRunner()
    result = runner.invoke(main, ['test'])
    assert result.exit_code != 0
    assert 'Error: Missing argument' in result.output


def test_cli_invalid_provider():
    """Confirm error if invalid provider supplied."""
    runner = CliRunner()
    result = runner.invoke(main, ['test', 'Provider'])
    assert result.exit_code != 0
    assert 'Error: Invalid value for' in result.output


def test_cli_invalid_distro():
    """Confirm error if invalid distro provided."""
    runner = CliRunner()
    result = runner.invoke(main, ['test', '-d', 'Distro'])
    assert result.exit_code != 0
    assert "Error: Invalid value for '-d' / '--distro'" \
        or 'Error: Invalid value for "-d" / "--distro"' in result.output


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
    """Test img_proof list endpoint."""
    runner = CliRunner()
    result = runner.invoke(main, ['list', 'tests/data/tests'])
    assert result.exit_code == 0


def test_cli_list_verbose():
    """Test img_proof list endpoint."""
    runner = CliRunner()
    result = runner.invoke(main, ['list', '-v', 'tests/data/tests'])
    assert result.exit_code == 0


def test_cli_results():
    """Test img_proof results endpoint."""
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


def test_cli_archive():
    """Test img_proof archive history sub command."""
    with open('tests/data/history.log') as f:
        log_file = f.readlines()

    with open('tests/data/history.results') as f:
        results_file = f.readlines()

    with open('tests/data/history.log') as f:
        log2_file = f.readlines()

    with open('tests/data/history.results') as f:
        results2_file = f.readlines()

    runner = CliRunner()
    with runner.isolated_filesystem():
        base_path = 'tests/data/ec2/ami-859bd1e5/i-44444444444444444/'
        os.makedirs(base_path)
        os.makedirs('archives')

        with open('tests/.history', 'w') as f:
            f.writelines([
                base_path + '20170626142856.log\n',
                base_path + '20170626142857.log\n'
            ])

        with open(base_path + '20170626142856.log', 'w') as f:
            f.writelines(log_file)

        with open(base_path + '20170626142856.results', 'w') as f:
            f.writelines(results_file)

        with open(base_path + '20170626142857.log', 'w') as f:
            f.writelines(log2_file)

        with open(base_path + '20170626142857.results', 'w') as f:
            f.writelines(results2_file)

        result = runner.invoke(
            main,
            [
                'results', '--history-log', 'tests/.history', 'archive',
                '--clear-log', 'archives/', 'archive_123'
            ]
        )
        output = result.output.split(':')[-1].strip()
        assert os.path.exists(output)

        result = runner.invoke(
            main,
            ['results', '--history-log', 'tests/.history', 'list']
        )
        assert "Path 'test/.history' does not exist." \
            or 'Path "test/.history" does not exist.' in result.output


def test_cli_archive_item():
    """Test img_proof archive specific history item."""
    with open('tests/data/history.log') as f:
        log_file = f.readlines()

    with open('tests/data/history.results') as f:
        results_file = f.readlines()

    runner = CliRunner()
    with runner.isolated_filesystem():
        base_path = 'tests/data/ec2/ami-859bd1e5/i-44444444444444444/'
        os.makedirs(base_path)
        os.makedirs('archives')

        with open('tests/.history', 'w') as f:
            f.writelines([
                base_path + '20170626142856.log\n',
                base_path + '20170626142857.log\n'
            ])

        with open(base_path + '20170626142856.log', 'w') as f:
            f.writelines(log_file)

        with open(base_path + '20170626142856.results', 'w') as f:
            f.writelines(results_file)

        result = runner.invoke(
            main,
            [
                'results', '--history-log', 'tests/.history', 'archive',
                '--clear-log', '-i', '2', 'archives/', 'archive_123'
            ]
        )

        output = result.output.split(':')[-1].strip()
        assert os.path.exists(output)

        result = runner.invoke(
            main,
            ['results', '--history-log', 'tests/.history', 'list']
        )
        expected_output = '1 tests/data/ec2/ami-859bd1e5/' \
            'i-44444444444444444/20170626142857.log\n'
        assert expected_output == result.output


def test_cli_archive_missing_item():
    """Test img_proof archive missing history item."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        base_path = 'tests/data/ec2/ami-859bd1e5/i-44444444444444444/'
        os.makedirs('archives')
        os.makedirs('tests')

        with open('tests/.history', 'w') as f:
            f.writelines([
                base_path + '20170626142856.log\n',
            ])

        result = runner.invoke(
            main,
            [
                'results', '--history-log', 'tests/.history', 'archive',
                '--clear-log', '-i', '1', 'archives/', 'archive_123'
            ]
        )

        assert result.output == \
            "Unable to archive history item: [Errno 2] No such file or " \
            "directory: 'tests/data/ec2/ami-859bd1e5/i-44444444444444444/" \
            "20170626142856.log'\n"


def test_cli_results_log():
    """Test img_proof results log display."""
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
    """Test img_proof results show handles exception."""
    runner = CliRunner()
    result = runner.invoke(
        main,
        ['results', '--history-log', 'tests/data/.history', 'show', '100']
    )
    assert result.exit_code != 0
    assert 'History result at index 100 does not exist.' in result.output


def test_cli_results_history():
    """Test img_proof results history."""
    runner = CliRunner()
    result = runner.invoke(
        main,
        ['results', '--history-log', 'tests/data/.history', 'list']
    )
    assert result.exit_code == 0


def test_cli_results_history_exception():
    """Test img_proof results history handles exception if file missing."""
    runner = CliRunner()
    result = runner.invoke(
        main,
        ['results', '--history-log', 'tests/data/.history', 'show', '3']
    )
    assert result.exit_code != 0
    assert 'Unable to process results file:' in result.output


def test_cli_results_history_log_exception():
    """Test img_proof results history handles exception if key missing."""
    runner = CliRunner()
    result = runner.invoke(
        main,
        ['results',
         '--history-log',
         'tests/data/.history',
         'show', '-l', '3']
    )
    assert result.exit_code != 0
    assert 'Unable to open results log file' in result.output


def test_cli_results_history_log():
    """Test img_proof results history."""
    runner = CliRunner()
    result = runner.invoke(
        main,
        ['results', '--history-log', 'tests/data/.history', 'show', '-l']
    )
    assert result.exit_code == 0


def test_cli_history():
    """Test img_proof list history sub command."""
    runner = CliRunner()
    result = runner.invoke(
        main,
        ['results', '--history-log', 'tests/data/.history', 'list']
    )
    assert result.exit_code == 0


def test_cli_clear_history():
    """Test img_proof clear history sub command."""
    lines = ''
    with open('tests/data/.history') as history_log:
        lines = history_log.readlines()

    runner = CliRunner()
    with runner.isolated_filesystem():
        try:
            os.makedirs('test')
        except OSError:
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
        assert "Path 'test/.history' does not exist." \
            or 'Path "test/.history" does not exist.' in result.output


def test_cli_delete_history_item():
    """Test img_proof delete history item at given index."""
    lines = []
    with open('tests/data/.history') as history_log:
        lines = history_log.readlines()

    before_count = len(lines)
    runner = CliRunner()
    with runner.isolated_filesystem():
        try:
            os.makedirs('test')
        except OSError:
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
    """Test img_proof history endpoint with empty history log."""
    runner = CliRunner()
    result = runner.invoke(
        main,
        ['results', '--history-log', 'tests/data/empty.history', 'list']
    )
    assert result.exit_code == 0


def test_cli_results_non_json():
    """Test img_proof results non json file provided."""
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
    """Test img_proof results json file missing key."""
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
    """Test img_proof cli license."""
    runner = CliRunner()
    result = runner.invoke(
        main,
        ['--license']
    )
    assert result.exit_code == 0
    assert result.output.strip() == 'GPLv3+'
