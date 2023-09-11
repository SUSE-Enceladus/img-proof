#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""img_proof CLI utils unit tests."""

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

import pytest

from img_proof.scripts import cli_utils
from click import BadParameter

DATA = {
    "info": {
        "platform": "azure",
        "image": "test_image",
        "instance": "azure-img_proof-test",
        "timestamp": "20170622155322",
        "distro": "SLES"
    },
    "tests": [{
        "nodeid": "img_proof/tests/test_sles.py::test_sles",
        "test_index": 0,
        "outcome": "passed"
    }, {
        "nodeid": "img_proof/tests/test_broken.py::test_broken",
        "test_index": 1,
        "outcome": "failed"
    }],
    "summary": {
        "duration": 0.0048158168791240234,
        "passed": 1,
        "failed": 1,
        "total": 2
    }
}


def test_echo_results():
    """Test cli utils echo results."""
    cli_utils.echo_results(DATA, False, verbose=True)


def test_cli_process_cpu_options():
    """Test process-cpu options"""
    TEST_DATA = [
        {
            'input': 'AmdSevSnp=enabled',
            'expected_output': {
                'AmdSevSnp': 'enabled'
            }
        },
        {
            'input': 'ExceptionShouldBeRaised'
        },
        {
            'input': 'AmdSevSnp=enabled,secondOption=secondValue',
            'expected_output': {
                'AmdSevSnp': 'enabled',
                'secondOption': 'secondValue'
            }
        },
    ]

    for data in TEST_DATA:
        if 'expected_output' in data:
            output = cli_utils.cli_process_cpu_options(
                {},
                'cpu-options',
                data['input']
            )

            assert data['expected_output'] == output
        else:
            with pytest.raises(BadParameter) as exc:
                cli_utils.cli_process_cpu_options(
                    {},
                    'cpu-options',
                    data['input']
                )
                assert str(exc).contains(data['input'])
