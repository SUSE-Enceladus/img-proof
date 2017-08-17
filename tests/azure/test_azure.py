#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""Integration tests for Azure provider."""

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

import vcr

from ipa import ipa_controller
from ipa.ipa_azure import AzureProvider
from ipa.ipa_provider import IpaProvider

from azure.servicemanagement import ServiceManagementService
from azurectl.account.service import AzureAccount

from unittest.mock import patch


@patch.object(AzureAccount, 'get_management_service')
@patch.object(AzureAccount, 'get_blob_service_host_base')
@patch('ipa.ipa_utils.generate_instance_name')
@patch.object(IpaProvider, '_run_tests')
@patch.object(IpaProvider, '_get_ssh_client')
@patch.object(time, 'sleep')
@vcr.use_cassette()
def test_azure_provider(mock_sleep,
                        mock_get_ssh_client,
                        mock_run_tests,
                        mock_generate_inst_name,
                        mock_get_blob_srv_host,
                        mock_get_mgm_service):
    """Test Azure Provider with a new instance."""
    # Mock SSH connection attempts
    mock_sleep.return_value = None
    mock_get_ssh_client.return_value = None
    mock_run_tests.return_value = 0

    # Mock out azure and azurectl
    mock_generate_inst_name.return_value = 'azure-ipa-test'
    mock_get_blob_srv_host.return_value = 'test.url'
    mock_get_mgm_service.return_value = ServiceManagementService(
        '77777777-7777-7777-7777-777777777777',
        'tests/azure/azure.config',
        'test.url'
    )

    status, results = ipa_controller.test_image(
        'Azure',
        config='tests/data/config',
        distro='SLES',
        history_log='tests/data/results/.history',
        image_id='b4590d9e3ed742e4a1d46e5424aa335e__'
                 'suse-sles-12-sp2-byos-v20170320',
        provider_config='tests/azure/azure.config',
        results_dir='tests/data/results',
        ssh_private_key='tests/data/ida_test',
        tests=['test_hard_reboot']
    )
    assert status == 0
