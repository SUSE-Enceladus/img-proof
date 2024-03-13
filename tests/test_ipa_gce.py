#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""img_proof GCE cloud unit tests."""

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

from img_proof.ipa_gce import GCECloud
from img_proof.ipa_exceptions import GCECloudException

from unittest.mock import MagicMock, patch


class TestGCECloud(object):
    """Test GCE cloud class."""

    @patch('img_proof.ipa_gce.AuthorizedSession')
    @patch('img_proof.ipa_gce.service_account')
    @patch.object(GCECloud, '_validate_region')
    @patch('img_proof.ipa_gce.compute_v1')
    def setup_method(
        self,
        method,
        mock_compute_v1,
        mock_validate_region,
        mock_service_account,
        mock_auth_session
    ):
        """Set up kwargs dict."""
        self.kwargs = {
            'config': 'tests/data/config',
            'distro_name': 'SLES',
            'image_id': 'fakeimage',
            'no_default_test_dirs': True,
            'ssh_private_key_file': 'tests/data/ida_test',
            'test_files': ['test_image'],
            'custom_args': {
                'service_account_file': 'tests/gce/service-account.json'
            },
            'instance_options': 'STACK_TYPE=IPV4_ONLY'
        }

        self.instances_client = MagicMock()
        self.zone_ops_client = MagicMock()
        self.zones_client = MagicMock()
        self.networks_client = MagicMock()
        self.subnet_client = MagicMock()
        self.machine_type_client = MagicMock()
        self.images_client = MagicMock()
        self.disks_client = MagicMock()
        mock_compute_v1.InstancesClient.return_value = self.instances_client
        mock_compute_v1.ZoneOperationsClient.return_value = \
            self.zone_ops_client
        mock_compute_v1.ZonesClient.return_value = self.zones_client

        service_account = MagicMock()
        mock_service_account.Credentials.\
            from_service_account_file.return_value = service_account

        self.cloud = GCECloud(**self.kwargs)

    def test_gce_exception_required_args(self):
        """Test an exception is raised if required args missing."""
        self.kwargs['custom_args']['service_account_file'] = None
        self.kwargs['ssh_private_key_file'] = None

        # Test service account file required
        with pytest.raises(GCECloudException) as error:
            GCECloud(**self.kwargs)

        assert str(error.value) == \
            'Service account file is required to connect to GCE.'

        self.kwargs['custom_args']['service_account_file'] = \
            'tests/gce/service-account.json'

        # Test ssh private key file required
        with pytest.raises(GCECloudException) as error:
            GCECloud(**self.kwargs)

        assert str(error.value) == \
            'SSH private key file is required to connect to instance.'

        self.kwargs['ssh_private_key_file'] = 'tests/data/ida_test'

    @patch('img_proof.ipa_gce.service_account')
    def test_gce_get_service_account_info_invalid(self, mock_service_account):
        """Test get credentials method with invalid service account."""
        self.cloud.service_account_file = \
            'tests/gce/invalid-service-account.json'

        with pytest.raises(GCECloudException) as error:
            self.cloud._get_credentials()

        msg = 'Service account JSON file is invalid for GCE. ' \
            'client_email key is expected. See getting started ' \
            'docs for information on GCE configuration.'
        assert str(error.value) == msg

    @patch('img_proof.ipa_gce.AuthorizedSession')
    @patch('img_proof.ipa_gce.service_account')
    def test_gce_get_creds_invalid(
        self,
        mock_service_account,
        mock_auth_session
    ):
        """Test get credentials method with exception."""
        session = MagicMock()
        session.get.side_effect = Exception('Invalid creds!')
        mock_auth_session.return_value = session

        with pytest.raises(GCECloudException) as error:
            self.cloud._get_credentials()

        msg = 'GCP authentication failed: Invalid creds!'
        assert str(error.value) == msg

    def test_gce_get_instance(self):
        """Test gce get instance method."""
        instance = MagicMock()
        self.instances_client.get.return_value = instance

        val = self.cloud._get_instance()

        assert val == instance

        self.cloud.running_instance_id = 'test-instance'
        self.instances_client.get.side_effect = Exception(
            'test-instance cannot be found.'
        )

        with pytest.raises(GCECloudException) as error:
            self.cloud._get_instance()

        exc = "Unable to retrieve instance: test-instance cannot be found."
        assert str(error.value) == exc

    @patch('img_proof.ipa_gce.compute_v1')
    def test_gce_get_network(self, mock_compute_v1):
        """Test GCE get network method."""
        mock_compute_v1.NetworksClient.return_value = self.networks_client
        network = MagicMock()
        self.networks_client.get.return_value = network

        result = self.cloud._get_network('test-network')

        assert result == network

        self.networks_client.get.side_effect = Exception(
            'Resource test-network not found.'
        )

        msg = 'Unable to retrieve network: Resource test-network not found.'
        with pytest.raises(GCECloudException) as error:
            self.cloud._get_network('test-network')

        assert msg == str(error.value)

    @patch('img_proof.ipa_gce.compute_v1')
    def test_gce_get_subnet(self, mock_compute_v1):
        """Test GCE get subnetwork method."""
        mock_compute_v1.SubnetworksClient.return_value = self.subnet_client
        subnetwork = MagicMock()
        self.subnet_client.get.return_value = subnetwork

        self.cloud.region = 'us-west-1a'
        result = self.cloud._get_subnet('test-subnet')

        assert result == subnetwork

        self.subnet_client.get.side_effect = Exception(
            'Resource test-subnet not found.'
        )

        msg = 'Unable to retrieve subnet: Resource test-subnet not found.'
        with pytest.raises(GCECloudException) as error:
            self.cloud._get_subnet('test-subnet')

        assert msg == str(error.value)

    @patch('img_proof.ipa_gce.compute_v1')
    def test_gce_get_instance_type(self, mock_compute_v1):
        """Test GCE get instance type method."""
        mock_compute_v1.MachineTypesClient.return_value = \
            self.machine_type_client
        machine_type = MagicMock()
        self.machine_type_client.get.return_value = machine_type

        result = self.cloud._get_instance_type('n1-standard-1')
        assert result == machine_type

        self.machine_type_client.get.side_effect = Exception(
            'Resource n1-standard-1 not found.'
        )

        msg = 'Unable to retrieve instance type: ' \
              'Resource n1-standard-1 not found.'
        with pytest.raises(GCECloudException) as error:
            self.cloud._get_instance_type('n1-standard-1')

        assert msg == str(error.value)

    @patch('img_proof.ipa_gce.compute_v1')
    def test_gce_get_image(self, mock_compute_v1):
        """Test GCE get image method."""
        mock_compute_v1.ImagesClient.return_value = self.images_client
        image = MagicMock()
        self.images_client.get.return_value = image

        result = self.cloud._get_image('fake-image-20200202')
        assert result == image

        self.images_client.get.side_effect = Exception(
            'Resource fake-image-20200202 not found.'
        )

        msg = 'Unable to retrieve image: ' \
              'Resource fake-image-20200202 not found.'
        with pytest.raises(GCECloudException) as error:
            self.cloud._get_image('fake-image-20200202')

        assert msg == str(error.value)

    @patch('img_proof.ipa_gce.compute_v1')
    def test_gce_get_disk(self, mock_compute_v1):
        """Test GCE get image method."""
        mock_compute_v1.DisksClient.return_value = self.disks_client
        disk = MagicMock()
        self.disks_client.get.return_value = disk

        result = self.cloud._get_disk('disk12')
        assert result == disk

        self.disks_client.get.side_effect = Exception(
            'Resource disk12 not found.'
        )

        msg = 'Unable to retrieve disk: ' \
              'Resource disk12 not found.'
        with pytest.raises(GCECloudException) as error:
            self.cloud._get_disk('disk12')

        assert msg == str(error.value)

    @patch.object(GCECloud, '_get_subnet')
    def test_get_network_config(self, mock_get_subnet):
        subnet = MagicMock()
        subnet.self_link = 'projects/test/regions/us-west1/subnetworks/sub-123'
        subnet.network.self_link = 'projects/test/global/networks/network'

        mock_get_subnet.return_value = subnet

        subnet_config = self.cloud._get_network_config(
            'sub-123',
            use_gvnic=True
        )

        assert subnet_config['network'] == subnet.network.self_link
        assert subnet_config['subnetwork'] == subnet.self_link

    def test_get_shielded_instance_config(self):
        si_config = self.cloud.get_shielded_instance_config()

        assert si_config['enable_secure_boot'] is False
        assert si_config['enable_vtpm']
        assert si_config['enable_integrity_monitoring']

    def test_get_instance_config(self):
        config = self.cloud.get_instance_config(
            'instance123',
            'n1-standard-1',
            [{}],
            'service-account-123@email.com',
            'image123',
            'secretkey',
            50,
            'x86_64',
            shielded_instance_config={'enable_secure_boot': True},
            sev='SEV_SNP',
            use_gvnic=True
        )

        assert 'metadata' in config
        assert 'service_accounts' in config
        assert 'machine_type' in config
        assert 'disks' in config
        assert 'network_interfaces' in config
        assert 'name' in config
        assert 'shielded_instance_config' in config

    @patch.object(GCECloud, '_wait_on_instance')
    @patch.object(GCECloud, 'wait_for_extended_operation')
    @patch.object(GCECloud, '_get_network')
    @patch.object(GCECloud, '_get_image')
    @patch.object(GCECloud, '_get_instance_type')
    @patch('img_proof.ipa_utils.generate_instance_name')
    def test_gce_launch_instance(
        self,
        mock_generate_instance_name,
        mock_get_instance_type,
        mock_get_image,
        mock_get_network,
        mock_wait_on_operation,
        mock_wait_on_instance
    ):
        """Test GCE launch instance method."""
        mock_generate_instance_name.return_value = 'test-instance'
        network = MagicMock()
        network.self_link = 'projects/test/global/networks/net1'
        mock_get_network.return_value = network

        image = MagicMock()
        image.self_link = 'projects/test/global/images/img-123'
        mock_get_image.return_value = image

        inst_type = MagicMock()
        inst_type.self_link = 'zones/us-west1-a/machineTypes/n1-standard-1'
        mock_get_instance_type.return_value = inst_type

        mock_wait_on_operation.return_value = None

        operation = MagicMock()
        operation.name = 'operation123'
        self.instances_client.insert.return_value = operation

        self.cloud.region = 'us-west1-a'

        self.cloud._launch_instance()

        assert self.cloud.running_instance_id == 'test-instance'
        assert mock_wait_on_instance.call_count == 1

        # Exception on operation

        self.instances_client.insert.side_effect = Exception(
            'Create failed!'
        )

        with pytest.raises(GCECloudException) as error:
            self.cloud._launch_instance()

        assert 'Failed to launch instance: Create failed!' == str(error.value)

    @patch.object(GCECloud, '_get_disk')
    @patch.object(GCECloud, '_get_instance')
    def test_gce_set_image_id(self, mock_get_instance, mock_get_disk):
        """Test gce cloud set image id method."""
        instance = MagicMock()
        disk = MagicMock()
        disk.device_name = 'disk123'
        disk.boot = True
        disk.source = (
            'https://www.googleapis.com/compute/v1/projects/'
            'test/zones/us-west1-a/disks/disk123'
        )
        disk.source_image = 'projects/suse/global/images/opensuse-leap-15.0'
        instance.disks = [disk]
        mock_get_instance.return_value = instance
        mock_get_disk.return_value = disk

        self.cloud._set_image_id()

        assert self.cloud.image_id == 'opensuse-leap-15.0'
        assert mock_get_instance.call_count == 1
        assert mock_get_disk.call_count == 1

    def test_gce_validate_region(self):
        """Test gce cloud set image id method."""
        zones_obj = MagicMock()
        zones_obj.return_value = None
        self.zones_client.get.return_value = zones_obj

        with pytest.raises(GCECloudException) as error:
            self.cloud._validate_region()

        assert str(error.value) == \
            'Zone is required for GCE cloud framework: Example: us-west1-a'

        self.cloud.region = 'fake'

        with pytest.raises(GCECloudException) as error:
            self.cloud._validate_region()

        assert str(error.value) == \
            'fake is not a valid GCE zone. Example: us-west1-a'

    @patch.object(GCECloud, '_get_instance')
    def test_gce_is_instance_running(self, mock_get_instance):
        """Test gce cloud is instance runnning method."""
        instance = MagicMock()
        instance.status = 'RUNNING'
        mock_get_instance.return_value = instance
        assert self.cloud._is_instance_running()
        assert mock_get_instance.call_count == 1

        instance.status = 'TERMINATED'
        mock_get_instance.return_value = instance
        assert not self.cloud._is_instance_running()

    @patch.object(GCECloud, '_get_instance')
    def test_gce_set_instance_ip(self, mock_get_instance):
        """Test gce cloud set instance ip method."""
        interface = MagicMock()
        interface.network_i_p = None
        interface.access_configs = []
        instance = MagicMock()
        instance.network_interfaces = [interface]
        mock_get_instance.return_value = instance

        self.cloud.running_instance_id = 'test'

        with pytest.raises(GCECloudException) as error:
            self.cloud._set_instance_ip()

        assert str(error.value) == \
            'IP address for instance: test cannot be found.'
        assert mock_get_instance.call_count == 1

        interface.network_i_p = '10.0.0.0'
        mock_get_instance.return_value = instance
        self.cloud._set_instance_ip()

        assert self.cloud.instance_ip == '10.0.0.0'

    @patch.object(GCECloud, '_wait_on_instance')
    def test_gce_start_instance(self, mock_wait_on_instance):
        """Test gce start instance method."""
        mock_wait_on_instance.return_value = None
        self.instances_client.start.return_value = None

        self.cloud._start_instance()

        assert self.instances_client.start.call_count == 1

    @patch.object(GCECloud, '_wait_on_instance')
    def test_gce_stop_instance(self, mock_wait_on_instance):
        """Test gce stop instance method."""
        mock_wait_on_instance.return_value = None
        self.instances_client.stop.return_value = None

        self.cloud._stop_instance()

        assert self.instances_client.stop.call_count == 1

    def test_gce_terminate_instance(self):
        """Test gce terminate instance method."""
        self.instances_client.delete.return_value = None

        self.cloud._terminate_instance()
        assert self.instances_client.delete.call_count == 1

    def test_gce_get_console_log(self):
        """Test gce get console log method."""
        operation = MagicMock()
        operation.content = 'some output'
        self.instances_client.get_serial_port_output.return_value = operation

        self.cloud.get_console_log()
        assert self.instances_client.get_serial_port_output.call_count == 1

    @patch('img_proof.ipa_gce.time')
    def test_wait_on_operation(self, mock_time):
        self.cloud.service_account_project = 'test_project'
        self.cloud.region = 'us-west1-a'

        mock_time.sleep.return_value = None
        mock_time.time.return_value = 10

        operation = MagicMock()
        operation.status = 'DONE'
        self.zone_ops_client.get.return_value = operation

        result = self.cloud._wait_on_operation('operation213')
        assert result.status == 'DONE'
        assert self.zone_ops_client.get.call_count == 1

    def test_wait_for_extended_operation(self):
        warning = MagicMock()
        warning.code = '123'
        warning.message = 'Something is wrong!'

        operation = MagicMock()
        operation.error_code = '412'
        operation.error_message = 'Operation failed!'
        operation.warnings = [warning]
        operation.result.return_value = False

        with pytest.raises(GCECloudException):
            self.cloud.wait_for_extended_operation(operation)
