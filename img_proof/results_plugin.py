# -*- coding: utf-8 -*-

"""
Pytest plugin to provide dict of test results.
"""

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

import time

from collections import defaultdict


class Report(object):
    """Pytest results plugin."""

    def __init__(self):
        """Initialize results plugin."""
        self.tests = defaultdict(dict)
        self.summary = defaultdict(int)
        self.test_index = 0
        self.report = {}

    def pytest_runtest_logreport(self, report):
        """Add individual test report to summary in dict."""
        if report.when == 'call':
            self.tests[report.nodeid]['test_index'] = self.test_index
            self.tests[report.nodeid]['name'] = report.nodeid
            self.test_index += 1

        if report.outcome != 'passed' or \
                'outcome' not in self.tests[report.nodeid]:
            # Setup or teardown may fail even if call passes
            self.tests[report.nodeid]['outcome'] = report.outcome

    def pytest_sessionfinish(self, session):
        """Finish session report."""
        stop = time.time()
        self.summary['duration'] = stop - self.start
        self.summary['num_tests'] = self.test_index

        for test in self.tests.values():
            self.summary[test['outcome']] += 1

        self.report = {
            'tests': self.tests.values(),
            'summary': self.summary
        }

    def pytest_sessionstart(self, session):
        """Set session start time."""
        self.start = time.time()
