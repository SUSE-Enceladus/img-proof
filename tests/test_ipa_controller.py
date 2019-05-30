#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""img_proof controller unit tests."""

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

from pytest import raises
from unittest.mock import patch

from img_proof.ipa_controller import collect_tests
from img_proof.ipa_exceptions import IpaControllerException


@patch('img_proof.ipa_controller.os')
def test_collect_tests_no_dirs(mock_os):
    """Test collect tests default directories do not exist."""
    mock_os.path.exists.return_value = False

    with raises(IpaControllerException):
        collect_tests(verbose=True)
