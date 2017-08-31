#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""Integration tests for EC2 provider."""

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

import time

import pytest
import vcr

from ipa import ipa_controller
from ipa.ipa_provider import IpaProvider

from unittest.mock import patch

boto3 = pytest.importorskip("boto3")


@patch.object(time, 'sleep')
@patch.object(IpaProvider, '_run_tests')
@patch.object(IpaProvider, '_get_ssh_client')
@patch('ipa.ipa_utils.get_host_key_fingerprint')
@vcr.use_cassette()
def test_ec2_provider(mock_get_host_key,
                      mock_get_ssh_client,
                      mock_run_tests,
                      mock_sleep):
    """Test EC2 Provider with new instance."""
    mock_get_host_key.return_value = b'04820482'
    mock_get_ssh_client.return_value = None
    mock_run_tests.return_value = 0
    mock_sleep.return_value = None

    status, results = ipa_controller.test_image(
        'EC2',
        account='bob',
        config='tests/data/config',
        distro='SLES',
        history_log='tests/data/results/.history',
        image_id='ami-859bd1e5',
        provider_config='tests/ec2/.ec2utils.conf',
        results_dir='tests/data/results',
        tests=['test_hard_reboot']
    )
    assert status == 0
