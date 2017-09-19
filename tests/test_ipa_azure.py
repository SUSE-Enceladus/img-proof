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
            'no_default_test_dirs': True,
            'provider_config': 'tests/azure/azure.config',
            'running_instance_id': 'fakeinstance',
            'ssh_private_key': 'tests/data/ida_test',
            'test_dirs': 'tests/data/tests',
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

    @patch.object(AzureProvider, '_wait_on_request')
    @patch.object(AzureProvider, '_get_virtual_machine')
    @patch.object(AzureProvider, '_get_cloud_service')
    @patch.object(AzureProvider, '_get_account')
    def test_azure_create_cloud_service(self,
                                        mock_get_account,
                                        mock_get_cloud_service,
                                        mock_get_vm,
                                        mock_wait_on_request):
        """Test create cloud service method."""
        account = MagicMock()
        cloud_service = MagicMock()
        cloud_service.create.return_value = '283e65be259bac8d9beb'
        vm = MagicMock()

        mock_get_account.return_value = account
        mock_get_cloud_service.return_value = cloud_service
        mock_get_vm.return_value = vm
        mock_wait_on_request.return_value = None

        provider = AzureProvider(**self.kwargs)
        service = provider._create_cloud_service('azure-test-instance')
        assert cloud_service == service
        assert mock_get_cloud_service.call_count == 1

    @patch.object(AzureProvider, '_get_virtual_machine')
    @patch('ipa.ipa_azure.AzurectlConfig')
    @patch('ipa.ipa_azure.AzureAccount')
    def test_azure_get_account(self,
                               mock_azure_account,
                               mock_azure_config,
                               mock_get_vm):
        """Test get account method."""
        account = MagicMock()
        config = MagicMock()
        vm = MagicMock()

        mock_azure_account.return_value = account
        mock_azure_config.return_value = config
        mock_get_vm.return_value = vm

        provider = AzureProvider(**self.kwargs)
        assert account == provider.account
        assert mock_azure_account.call_count == 1

    @patch.object(AzureProvider, '_get_virtual_machine')
    @patch.object(AzureProvider, '_get_account')
    @patch('ipa.ipa_azure.CloudService')
    def test_azure_get_cloud_service(self,
                                     mock_cloud_service,
                                     mock_get_account,
                                     mock_get_vm):
        """Test get cloud service method."""
        account = MagicMock()
        cloud_service = MagicMock()
        vm = MagicMock()

        mock_get_account.return_value = account
        mock_cloud_service.return_value = cloud_service
        mock_get_vm.return_value = vm

        provider = AzureProvider(**self.kwargs)
        service = provider._get_cloud_service()
        assert service == cloud_service
        assert mock_cloud_service.call_count == 1

    @patch.object(AzureProvider, '_get_virtual_machine')
    @patch.object(AzureProvider, '_get_account')
    def test_azure_get_instance_state(self,
                                      mock_get_account,
                                      mock_get_vm):
        """Test get instance state method."""
        account = MagicMock()
        vm = MagicMock()
        vm.instance_status.return_value = 'ReadyRole'

        mock_get_account.return_value = account
        mock_get_vm.return_value = vm

        provider = AzureProvider(**self.kwargs)
        assert provider._get_instance_state() == 'ReadyRole'
        assert vm.instance_status.call_count == 1

    @patch.object(AzureProvider, '_get_account')
    @patch('ipa.ipa_azure.VirtualMachine')
    def test_azure_get_virtual_machine(self,
                                       mock_virtual_machine,
                                       mock_get_account):
        """Test get virtual machine method."""
        account = MagicMock()
        vm = MagicMock()

        mock_get_account.return_value = account
        mock_virtual_machine.return_value = vm

        provider = AzureProvider(**self.kwargs)
        assert vm == provider.vm
        assert mock_virtual_machine.call_count == 1

    @patch.object(AzureProvider, '_wait_on_instance')
    @patch.object(AzureProvider, '_get_virtual_machine')
    @patch.object(AzureProvider, '_get_account')
    @patch.object(AzureProvider, '_create_cloud_service')
    @patch('ipa.ipa_utils.generate_instance_name')
    def test_azure_launch_instance(self,
                                   mock_generate_instance_name,
                                   mock_get_account,
                                   mock_create_cloud_service,
                                   mock_get_vm,
                                   mock_wait_on_instance):
        """Test launch instance method."""
        account = MagicMock()
        cloud_service = MagicMock()
        config = MagicMock()
        fingerprint = MagicMock()
        net_config = MagicMock()
        ssh_endpoint = MagicMock()
        vm = MagicMock()

        cloud_service.add_certificate.return_value = fingerprint

        vm.create_linux_configuration.return_value = config
        vm.create_instance.return_value = None
        vm.create_network_configuration.return_value = net_config
        vm.create_network_endpoint.return_value = ssh_endpoint

        mock_create_cloud_service.return_value = cloud_service
        mock_get_account.return_value = account
        mock_get_vm.return_value = vm
        mock_wait_on_instance.return_value = None
        mock_generate_instance_name.return_value = 'azure-test-instance'

        provider = AzureProvider(**self.kwargs)
        provider._launch_instance()
        assert provider.running_instance_id == 'azure-test-instance'
        assert vm.create_instance.call_count == 1

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

    @patch.object(AzureProvider, '_wait_on_instance')
    @patch.object(AzureProvider, '_get_virtual_machine')
    @patch.object(AzureProvider, '_get_account')
    def test_azure_start_instance(self,
                                  mock_get_account,
                                  mock_get_vm,
                                  mock_wait_on_instance):
        """Test start instance method."""
        account = MagicMock()
        vm = MagicMock()

        vm.start_instance.return_value = None

        mock_get_account.return_value = account
        mock_get_vm.return_value = vm
        mock_wait_on_instance.return_value = None

        provider = AzureProvider(**self.kwargs)
        provider._start_instance()
        assert vm.start_instance.call_count == 1

    @patch.object(AzureProvider, '_wait_on_instance')
    @patch.object(AzureProvider, '_get_virtual_machine')
    @patch.object(AzureProvider, '_get_account')
    def test_azure_stop_instance(self,
                                 mock_get_account,
                                 mock_get_vm,
                                 mock_wait_on_instance):
        """Test stop instance method."""
        account = MagicMock()
        vm = MagicMock()

        vm.shutdown_instance.return_value = None

        mock_get_account.return_value = account
        mock_get_vm.return_value = vm
        mock_wait_on_instance.return_value = None

        provider = AzureProvider(**self.kwargs)
        provider._stop_instance()
        assert vm.shutdown_instance.call_count == 1

    @patch.object(AzureProvider, '_get_cloud_service')
    @patch.object(AzureProvider, '_get_virtual_machine')
    @patch.object(AzureProvider, '_get_account')
    def test_azure_terminate_instance(self,
                                      mock_get_account,
                                      mock_get_vm,
                                      mock_get_cloud_service):
        """Test terminate instance method."""
        account = MagicMock()
        cloud_service = MagicMock()
        vm = MagicMock()

        cloud_service.delete.return_value = None

        mock_get_account.return_value = account
        mock_get_cloud_service.return_value = cloud_service
        mock_get_vm.return_value = vm

        provider = AzureProvider(**self.kwargs)
        provider._terminate_instance()
        assert cloud_service.delete.call_count == 1

    @patch.object(AzureProvider, '_get_instance_state')
    @patch.object(AzureProvider, '_get_virtual_machine')
    @patch.object(AzureProvider, '_get_account')
    @patch('time.sleep')
    def test_azure_wait_on_instance(self,
                                    mock_sleep,
                                    mock_get_account,
                                    mock_get_vm,
                                    mock_get_instance_state):
        """Test wait on instance method."""
        account = MagicMock()
        vm = MagicMock()

        mock_get_account.return_value = account
        mock_get_vm.return_value = vm
        mock_get_instance_state.return_value = 'Stopped'
        mock_sleep.return_value = None

        provider = AzureProvider(**self.kwargs)
        provider._wait_on_instance('Stopped')
        assert mock_get_instance_state.call_count == 1

    @patch('ipa.ipa_azure.RequestResult')
    @patch.object(AzureProvider, '_get_virtual_machine')
    @patch.object(AzureProvider, '_get_account')
    def test_azure_wait_on_request(self,
                                   mock_get_account,
                                   mock_get_vm,
                                   mock_request_result):
        """Test wait on request method."""
        account = MagicMock()
        request_result = MagicMock()
        service = MagicMock()
        vm = MagicMock()

        account.get_management_service.return_value = service
        request_result.wait_for_request_completion.return_value = None

        mock_get_account.return_value = account
        mock_get_vm.return_value = vm
        mock_request_result.return_value = request_result

        provider = AzureProvider(**self.kwargs)
        provider._wait_on_request('12345')
        assert request_result.wait_for_request_completion.call_count == 1
