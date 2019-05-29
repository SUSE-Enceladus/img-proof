#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""Pytest results plugin tests."""

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

import shlex

import pytest

from img_proof.results_plugin import Report


def test_pytest_json_results():
    """Test json results output."""
    args = "-v tests/data/tests/test_pytest_json_results.py"
    cmds = shlex.split(args)
    plugin = Report()

    result = pytest.main(cmds, plugins=[plugin])

    assert result != 0
    assert plugin.report['summary']['passed'] == 2
    assert plugin.report['summary']['failed'] == 1
    assert plugin.report['summary']['num_tests'] == 3
