#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""img_proof azure provider unit tests."""

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

import pytest

from img_proof.ipa_azure import AzureCloud
from img_proof.ipa_exceptions import AzureCloudException

from unittest.mock import MagicMock, patch


class TestAzureProvider(object):
    """Test Azure provider class."""

    def setup(self):
        self.client = MagicMock()

    def setup_method(self, method):
        """Set up kwargs dict."""
        self.kwargs = {
            'config': 'tests/data/config',
            'distro_name': 'sles',
            'image_id': 'another:fake:image:id',
            'no_default_test_dirs': True,
            'running_instance_id': 'fakeinstance',
            'service_account_file': 'tests/azure/test-sa.json',
            'ssh_private_key_file': 'tests/data/ida_test',
            'test_dirs': 'tests/data/tests',
            'test_files': ['test_image']
        }

    @patch.object(AzureCloud, '_get_management_client')
    @patch.object(AzureCloud, '_get_ssh_public_key')
    def helper_get_provider(self, mock_get_ssh_pub_key, mock_get_client):
        mock_get_client.return_value = self.client
        return AzureCloud(**self.kwargs)

    def test_azure_exception_required_args(self):
        """Test an exception is raised if required args missing."""
        self.kwargs['ssh_private_key_file'] = None
        msg = 'SSH private key file is required to connect to instance.'

        # Test ssh private key file required
        with pytest.raises(AzureCloudException) as error:
            AzureCloud(**self.kwargs)

        assert str(error.value) == msg

    @patch('img_proof.ipa_azure.get_client_from_auth_file')
    def test_get_management_client(self, mock_get_client):
        client = MagicMock()
        mock_get_client.return_value = client

        client_class = MagicMock()

        provider = self.helper_get_provider()
        result = provider._get_management_client(client_class)

        assert result == client

    @patch('img_proof.ipa_azure.get_client_from_auth_file')
    def test_get_management_client_json_error(self, mock_get_client):
        client_class = MagicMock()
        mock_get_client.side_effect = ValueError(
            'Not valid'
        )

        provider = self.helper_get_provider()

        with pytest.raises(AzureCloudException) as error:
            provider._get_management_client(client_class)

        assert str(error.value) == 'Service account file format is invalid: ' \
            'Not valid.'

    @patch('img_proof.ipa_azure.get_client_from_auth_file')
    def test_get_management_client_key_error(self, mock_get_client):
        client_class = MagicMock()
        mock_get_client.side_effect = KeyError('subscriptionId')

        provider = self.helper_get_provider()

        with pytest.raises(AzureCloudException) as error:
            provider._get_management_client(client_class)

        assert str(error.value) == "Service account file missing key: " \
            "'subscriptionId'."

    @patch('img_proof.ipa_azure.get_client_from_auth_file')
    def test_get_management_client_exception(self, mock_get_client):
        client_class = MagicMock()
        mock_get_client.side_effect = Exception('Not valid')

        provider = self.helper_get_provider()

        with pytest.raises(AzureCloudException) as error:
            provider._get_management_client(client_class)

        assert str(error.value) == 'Unable to create resource management ' \
            'client: Not valid.'

    @patch('img_proof.ipa_azure.ipa_utils.get_public_ssh_key')
    def test_get_ssh_public_key(self, mock_get_pub_key):
        mock_get_pub_key.return_value = b'pub-key'
        provider = self.helper_get_provider()
        key = provider._get_ssh_public_key()

        assert key == 'pub-key'

    def test_azure_is_instance_running(self):
        """Test is instance running method."""
        instance = MagicMock()
        status = MagicMock()
        status.code = 'PowerState'
        status.display_status = 'VM running'
        instance.instance_view.statuses = [status]

        self.client.virtual_machines.get.return_value = instance

        provider = self.helper_get_provider()
        assert provider._is_instance_running()

    @patch.object(AzureCloud, '_wait_on_instance')
    @patch('img_proof.ipa_utils.generate_instance_name')
    def test_azure_launch_instance_exception(
        self, mock_generate_instance_name, mock_wait_on_instance
    ):
        """Test launch instance method."""
        mock_generate_instance_name.return_value = 'azure-test-instance'
        self.client.resource_groups.create_or_update.side_effect = Exception(
            'Cannot create resource group!'
        )
        self.client.resource_groups.delete.side_effect = Exception(
            'Cannot delete resource group!'
        )

        provider = self.helper_get_provider()

        with pytest.raises(AzureCloudException):
            provider._launch_instance()

    @patch.object(AzureCloud, '_wait_on_instance')
    @patch('img_proof.ipa_utils.generate_instance_name')
    def test_azure_launch_instance(
            self, mock_generate_instance_name, mock_wait_on_instance
    ):
        """Test launch instance method."""
        mock_generate_instance_name.return_value = 'azure-test-instance'

        provider = self.helper_get_provider()
        provider._launch_instance()

        assert self.client.network_interfaces.create_or_update.call_count == 1
        assert self.client.public_ip_addresses.create_or_update.call_count == 1
        assert self.client.resource_groups.create_or_update.call_count == 1
        assert self.client.virtual_machines.create_or_update.call_count == 1
        assert self.client.subnets.create_or_update.call_count == 1
        assert self.client.virtual_networks.create_or_update.call_count == 1
        assert provider.running_instance_id == 'azure-test-instance'

    @patch.object(AzureCloud, '_wait_on_instance')
    @patch('img_proof.ipa_utils.generate_instance_name')
    def test_create_storage_profile(
            self, mock_generate_instance_name, mock_wait_on_instance
    ):
        """Test launch instance method."""
        mock_generate_instance_name.return_value = 'azure-test-instance'
        self.kwargs['image_id'] = 'custom-image.vhd'

        image = MagicMock()
        image.name = 'custom-image.vhd'
        image.id = '/id/custom-image.vhd'
        self.client.images.list.return_value = [image]

        provider = self.helper_get_provider()

        provider._process_image_id()
        storage_profile = provider._create_storage_profile()

        assert storage_profile['image_reference']['id'] == \
            '/id/custom-image.vhd'

    def test_process_image_id(self):
        provider = self.helper_get_provider()
        provider._process_image_id()

        assert provider.image_publisher == 'another'
        assert provider.image_offer == 'fake'
        assert provider.image_sku == 'image'
        assert provider.image_version == 'id'

    def test_process_custom_image_id(self):
        provider = self.helper_get_provider()
        provider.image_id = 'custom-image.vhd'

        provider._process_image_id()
        assert provider.image_publisher is None

    def test_set_default_resource_names(self):
        provider = self.helper_get_provider()
        provider._set_default_resource_names()

        assert provider.ip_config_name == 'fakeinstance-ip-config'
        assert provider.nic_name == 'fakeinstance-nic'
        assert provider.public_ip_name == 'fakeinstance-public-ip'

    @patch.object(AzureCloud, '_get_instance')
    def test_azure_set_image_id(self, mock_get_instance):
        """Test set image id method."""
        self.kwargs['image_id'] = None

        image_reference = MagicMock()
        image_reference.publisher = 'another'
        image_reference.offer = 'fake'
        image_reference.sku = 'image'
        image_reference.version = 'id'

        instance = MagicMock()
        instance.storage_profile.image_reference = image_reference

        mock_get_instance.return_value = instance

        provider = self.helper_get_provider()
        provider._set_image_id()

        assert provider.image_id == 'another:fake:image:id'

    @patch('img_proof.ipa_utils.generate_instance_name')
    def test_azure_set_instance_ip_exception(
        self, mock_generate_instance_name
    ):
        """Test set instance ip exception."""
        mock_generate_instance_name.return_value = 'azure-test-instance'
        provider = self.helper_get_provider()

        self.client.public_ip_addresses.get.side_effect = Exception(
            'IP not found'
        )
        self.client.network_interfaces.get.side_effect = Exception(
            'IP not found'
        )

        with pytest.raises(AzureCloudException) as error:
            provider._set_instance_ip()

        assert str(error.value) == \
            'Unable to retrieve instance IP address: IP not found.'

    @patch('img_proof.ipa_utils.generate_instance_name')
    def test_azure_set_instance_ip(self, mock_generate_instance_name):
        """Test set instance ip method."""
        mock_generate_instance_name.return_value = 'azure-test-instance'
        provider = self.helper_get_provider()

        ip_address = MagicMock()
        ip_address.ip_address = '10.0.0.1'
        self.client.public_ip_addresses.get.return_value = ip_address

        provider._set_instance_ip()
        assert provider.instance_ip == '10.0.0.1'

    def test_azure_start_instance(self):
        """Test start instance method."""
        provider = self.helper_get_provider()
        provider.running_instance_id = 'img_proof-test-instance'

        provider._start_instance()
        self.client.virtual_machines.start.assert_called_once_with(
            'img_proof-test-instance', 'img_proof-test-instance'
        )

        # Test exception
        self.client.virtual_machines.start.side_effect = Exception(
            'Instance not found'
        )

        with pytest.raises(AzureCloudException) as error:
            provider._start_instance()

        assert str(error.value) == 'Unable to start instance: ' \
            'Instance not found.'

    def test_azure_stop_instance(self):
        """Test stop instance method."""
        provider = self.helper_get_provider()
        provider.running_instance_id = 'img_proof-test-instance'

        provider._stop_instance()
        self.client.virtual_machines.power_off.assert_called_once_with(
            'img_proof-test-instance', 'img_proof-test-instance'
        )

        # Test exception
        self.client.virtual_machines.power_off.side_effect = Exception(
            'Instance not found'
        )

        with pytest.raises(AzureCloudException) as error:
            provider._stop_instance()

        assert str(error.value) == 'Unable to stop instance: ' \
            'Instance not found.'

    def test_azure_terminate_instance(self):
        """Test terminate instance method."""
        provider = self.helper_get_provider()
        provider.running_instance_id = 'img_proof-test-instance'

        provider._terminate_instance()
        self.client.resource_groups.delete.assert_called_once_with(
            'img_proof-test-instance'
        )

        # Test exception
        self.client.resource_groups.delete.side_effect = Exception(
            'Instance not found'
        )

        with pytest.raises(AzureCloudException) as error:
            provider._terminate_instance()

        assert str(error.value) == 'Unable to terminate resource group: ' \
            'Instance not found.'
