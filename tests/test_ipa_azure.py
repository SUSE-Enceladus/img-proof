#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""Ipa azure provider unit tests."""

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

from ipa.ipa_azure import AzureProvider
from ipa.ipa_exceptions import AzureProviderException

import pytest

from unittest.mock import MagicMock, patch


class TestAzureProvider(object):
    """Test Azure provider class."""

    def setup_method(self, method):
        """Set up kwargs dict."""
        self.kwargs = {
            'config': 'tests/data/config',
            'distro_name': 'SLES',
            'image_id': 'fakeimage',
            'provider_config': 'tests/azure/azure.config',
            'running_instance_id': 'fakeinstance',
            'ssh_private_key': 'tests/data/ida_test',
            'test_dirs': ['tests/data/tests'],
            'test_files': ['test_image']
        }

    def test_azure_exception_required_args(self):
        """Test an exception is raised if required args missing."""
        self.kwargs['ssh_private_key'] = None
        msg = 'SSH private key file is required to connect to instance.'

        # Test ssh private key file required
        with pytest.raises(AzureProviderException) as error:
            AzureProvider(**self.kwargs)

        assert str(error.value) == msg

    @patch.object(AzureProvider, '_get_virtual_machine')
    @patch.object(AzureProvider, '_get_account')
    def test_azure_generate_instance_name(self,
                                          mock_get_account,
                                          mock_get_vm):
        """Test generate instance name method."""
        account = MagicMock()
        vm = MagicMock()
        mock_get_account.return_value = account
        mock_get_vm.return_value = vm

        provider = AzureProvider(**self.kwargs)
        name = provider._generate_instance_name()
        assert len(name) == 20
        assert name.startswith('azure-ipa-test-')

    @patch.object(AzureProvider, '_get_virtual_machine')
    @patch.object(AzureProvider, '_get_instance_state')
    @patch.object(AzureProvider, '_get_account')
    def test_azure_instance_runnning_undefined(self,
                                               mock_get_account,
                                               mock_get_instance_state,
                                               mock_get_vm):
        """Test instance running undefined state."""
        account = MagicMock()
        vm = MagicMock()
        mock_get_account.return_value = account
        mock_get_instance_state.return_value = 'Undefined'
        mock_get_vm.return_value = vm

        provider = AzureProvider(**self.kwargs)

        with pytest.raises(AzureProviderException) as error:
            provider._is_instance_running()

        assert str(error.value) == \
            'Instance with name: fakeinstance, cannot be found.'
        assert mock_get_instance_state.call_count == 1

    @patch.object(AzureProvider, '_get_virtual_machine')
    @patch.object(AzureProvider, '_get_instance_state')
    @patch.object(AzureProvider, '_get_account')
    def test_azure_instance_runnning(self,
                                     mock_get_account,
                                     mock_get_instance_state,
                                     mock_get_vm):
        """Test instance running undefined state."""
        account = MagicMock()
        vm = MagicMock()
        mock_get_account.return_value = account
        mock_get_instance_state.return_value = 'ReadyRole'
        mock_get_vm.return_value = vm

        provider = AzureProvider(**self.kwargs)

        assert provider._is_instance_running()
        assert mock_get_instance_state.call_count == 1
        mock_get_instance_state.reset_mock()

        mock_get_instance_state.return_value = 'StoppedDeallocated'
        assert not provider._is_instance_running()
        assert mock_get_instance_state.call_count == 1

    @patch.object(AzureProvider, '_get_virtual_machine')
    @patch.object(AzureProvider, '_get_account')
    def test_azure_set_image_id_exception(self,
                                          mock_get_account,
                                          mock_get_vm):
        """Test set image id exception."""
        account = MagicMock()
        vm = MagicMock()
        properties = MagicMock()
        properties.deployments = []
        vm.service.get_hosted_service_properties.return_value = properties

        mock_get_account.return_value = account
        mock_get_vm.return_value = vm

        provider = AzureProvider(**self.kwargs)

        with pytest.raises(AzureProviderException) as error:
            provider._set_image_id()

        assert str(error.value) == \
            'Image name for instance cannot be found.'

    @patch.object(AzureProvider, '_get_virtual_machine')
    @patch.object(AzureProvider, '_get_account')
    def test_azure_set_image_id(self,
                                mock_get_account,
                                mock_get_vm):
        """Test set image id method."""
        account = MagicMock()
        vm = MagicMock()
        properties = MagicMock()
        deployment = MagicMock()
        role = MagicMock()
        role.os_virtual_hard_disk.source_image_name = 'fakeimage'
        deployment.role_list = [role]
        properties.deployments = [deployment]
        vm.service.get_hosted_service_properties.return_value = properties

        mock_get_account.return_value = account
        mock_get_vm.return_value = vm

        provider = AzureProvider(**self.kwargs)
        provider._set_image_id()

        assert provider.image_id == 'fakeimage'

    @patch.object(AzureProvider, '_get_virtual_machine')
    @patch.object(AzureProvider, '_get_cloud_service')
    @patch.object(AzureProvider, '_get_account')
    def test_azure_set_instance_ip_exception(self,
                                             mock_get_account,
                                             mock_get_cloud_service,
                                             mock_get_vm):
        """Test set instance ip exception."""
        cloud_service = MagicMock()
        cloud_service.get_properties.return_value = {'deployments': []}
        mock_get_cloud_service.return_value = cloud_service

        account = MagicMock()
        mock_get_account.return_value = account

        vm = MagicMock()
        mock_get_vm.return_value = vm

        provider = AzureProvider(**self.kwargs)

        with pytest.raises(AzureProviderException) as error:
            provider._set_instance_ip()

        assert str(error.value) == \
            'IP address for instance cannot be found.'
        assert mock_get_cloud_service.call_count == 1

    @patch.object(AzureProvider, '_get_virtual_machine')
    @patch.object(AzureProvider, '_get_cloud_service')
    @patch.object(AzureProvider, '_get_account')
    def test_azure_set_instance_ip(self,
                                   mock_get_account,
                                   mock_get_cloud_service,
                                   mock_get_vm):
        """Test set instance ip method."""
        cloud_service = MagicMock()
        cloud_service.get_properties.return_value = {
            'deployments': [{'virtual_ips': [{'address': '127.0.0.1'}]}]
        }
        mock_get_cloud_service.return_value = cloud_service

        account = MagicMock()
        mock_get_account.return_value = account

        vm = MagicMock()
        mock_get_vm.return_value = vm

        provider = AzureProvider(**self.kwargs)
        provider._set_instance_ip()

        assert provider.instance_ip == '127.0.0.1'
        assert mock_get_cloud_service.call_count == 1
