# -*- coding: utf-8 -*-
#
# Copyright (c) 2017 SUSE LLC
#
# This file is part of ipa.
#
# See LICENSE for license information.


class Tap(object):

    def __init__(self):
        super(Tap, self).__init__()

    def test_image(self):
        """Creates a cloud provider instance and initiates testing."""

    def list_tests(self):
        """Returns a list of test files and/or tests."""

    def collect_results(self):
        """Returns the result (pass/fail) or verbose results."""

