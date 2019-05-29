# -*- coding: utf-8 -*-

"""Collect test items plugin."""

# Copyright (c) 2019 SUSE LLC
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

from collections import defaultdict


class CollectItemsPlugin(object):
    """Collect test items pytest plugin class."""

    def __init__(self):
        """Intialize collected dictionary."""
        self.collected = defaultdict(list)

    def pytest_collection_modifyitems(self, items):
        """
        Plugin to return a list of test cases from pytest collection.

        The list returned contains all test cases and classes in each
        test file found.
        """
        for item in items:
            test_class = None
            try:
                path, test_class, parens, test_case = item.nodeid.split('::')
            except ValueError:
                path, test_case = item.nodeid.split('::')

            test_file = path.split(os.sep)[-1].replace('.py', '')

            # Filter None and empty string values
            self.collected[test_file].append(
                '::'.join(filter(None, [test_file, test_class, test_case]))
            )
