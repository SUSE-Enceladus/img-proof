#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""Ipa CLI utils unit tests."""

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

from ipa.scripts import cli_utils

DATA = {
    "info": {
        "platform": "azure",
        "image": "test_image",
        "instance": "azure-ipa-test",
        "timestamp": "20170622155322",
        "distro": "SLES"
    },
    "tests": [{
        "name": "ipa/tests/test_sles.py::test_sles",
        "test_index": 0,
        "outcome": "passed"
    }, {
        "name": "ipa/tests/test_broken.py::test_broken",
        "test_index": 1,
        "outcome": "failed"
    }],
    "summary": {
        "duration": 0.0048158168791240234,
        "passed": 1,
        "failed": 1,
        "num_tests": 2
    }
}


def test_echo_results():
    """Test cli utils echo results."""
    cli_utils.echo_results(DATA, False, verbose=True)
