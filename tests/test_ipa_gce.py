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

import json
import pytest

from img_proof.ipa_gce import GCECloud
from img_proof.ipa_exceptions import GCECloudException, IpaRetryableError

from unittest.mock import MagicMock, patch

from googleapiclient.errors import HttpError


def get_http_error(msg, status='404'):
    resp = MagicMock()
    resp.status = status

    content = {
        'error': {
            'code': int(status),
            'message': msg
        }
    }

    return HttpError(resp, json.dumps(content).encode())


class TestGCECloud(object):
    """Test GCE cloud class."""

    @patch('img_proof.ipa_gce.service_account')
    @patch.object(GCECloud, '_validate_region')
    @patch('img_proof.ipa_gce.discovery')
    def setup(
        self,
        mock_discovery,
        mock_validate_region,
        mock_service_account
    ):
        """Set up kwargs dict."""
        self.kwargs = {
            'config': 'tests/data/config',
            'distro_name': 'SLES',
            'image_id': 'fakeimage',
            'no_default_test_dirs': True,
            'service_account_file': 'tests/gce/service-account.json',
            'ssh_private_key_file': 'tests/data/ida_test',
            'test_files': ['test_image']
        }

        driver = MagicMock()
        mock_discovery.build.return_value = driver

        service_account = MagicMock()
        mock_service_account.Credentials.\
            from_service_account_file.return_value = service_account

        self.cloud = GCECloud(**self.kwargs)

    def test_gce_exception_required_args(self):
        """Test an exception is raised if required args missing."""
        self.kwargs['service_account_file'] = None
        self.kwargs['ssh_private_key_file'] = None

        # Test service account file required
        with pytest.raises(GCECloudException) as error:
            GCECloud(**self.kwargs)

        assert str(error.value) == \
            'Service account file is required to connect to GCE.'

        self.kwargs['service_account_file'] = 'tests/gce/service-account.json'

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

    def test_gce_get_instance(self):
        """Test gce get instance method."""
        instance = MagicMock()
        instances_obj = MagicMock()
        operation = MagicMock()
        operation.execute.return_value = instance
        instances_obj.get.return_value = operation
        self.cloud.compute_driver.instances.return_value = instances_obj

        val = self.cloud._get_instance()

        assert val == instance

        self.cloud.running_instance_id = 'test-instance'
        instances_obj.get.side_effect = get_http_error(
            'test-instance cannot be found.'
        )

        with pytest.raises(GCECloudException) as error:
            self.cloud._get_instance()

        exc = "Unable to retrieve instance: test-instance cannot be found."
        assert str(error.value) == exc

    def test_gce_get_network(self):
        """Test GCE get network method."""
        network = MagicMock()
        networks_obj = MagicMock()
        operation = MagicMock()
        operation.execute.return_value = network
        networks_obj.get.return_value = operation
        self.cloud.compute_driver.networks.return_value = networks_obj

        result = self.cloud._get_network('test-network')

        assert result == network

        networks_obj.get.side_effect = get_http_error(
            'Resource test-network not found.'
        )

        msg = 'Unable to retrieve network: Resource test-network not found.'
        with pytest.raises(GCECloudException) as error:
            self.cloud._get_network('test-network')

        assert msg == str(error.value)

    def test_gce_get_subnet(self):
        """Test GCE get subnetwork method."""
        subnetwork = MagicMock()
        subnet_obj = MagicMock()
        operation = MagicMock()
        operation.execute.return_value = subnetwork
        subnet_obj.get.return_value = operation
        self.cloud.compute_driver.subnetworks.return_value = subnet_obj

        self.cloud.region = 'us-west-1a'
        result = self.cloud._get_subnet('test-subnet')

        assert result == subnetwork

        subnet_obj.get.side_effect = get_http_error(
            'Resource test-subnet not found.'
        )

        msg = 'Unable to retrieve subnet: Resource test-subnet not found.'
        with pytest.raises(GCECloudException) as error:
            self.cloud._get_subnet('test-subnet')

        assert msg == str(error.value)

    def test_gce_get_instance_type(self):
        """Test GCE get instance type method."""
        machine_type = MagicMock()
        machine_type_obj = MagicMock()
        operation = MagicMock()
        operation.execute.return_value = machine_type
        machine_type_obj.get.return_value = operation
        self.cloud.compute_driver.machineTypes.return_value = machine_type_obj

        result = self.cloud._get_instance_type('n1-standard-1')
        assert result == machine_type

        machine_type_obj.get.side_effect = get_http_error(
            'Resource n1-standard-1 not found.'
        )

        msg = 'Unable to retrieve instance type: ' \
              'Resource n1-standard-1 not found.'
        with pytest.raises(GCECloudException) as error:
            self.cloud._get_instance_type('n1-standard-1')

        assert msg == str(error.value)

    def test_gce_get_image(self):
        """Test GCE get image method."""
        image = MagicMock()
        image_obj = MagicMock()
        operation = MagicMock()
        operation.execute.return_value = image
        image_obj.get.return_value = operation
        self.cloud.compute_driver.images.return_value = image_obj

        result = self.cloud._get_image('fake-image-20200202')
        assert result == image

        image_obj.get.side_effect = get_http_error(
            'Resource fake-image-20200202 not found.'
        )

        msg = 'Unable to retrieve image: ' \
              'Resource fake-image-20200202 not found.'
        with pytest.raises(GCECloudException) as error:
            self.cloud._get_image('fake-image-20200202')

        assert msg == str(error.value)

    def test_gce_get_disk(self):
        """Test GCE get image method."""
        disk = MagicMock()
        disk_obj = MagicMock()
        operation = MagicMock()
        operation.execute.return_value = disk
        disk_obj.get.return_value = operation
        self.cloud.compute_driver.disks.return_value = disk_obj

        result = self.cloud._get_disk('disk12')
        assert result == disk

        disk_obj.get.side_effect = get_http_error(
            'Resource disk12 not found.'
        )

        msg = 'Unable to retrieve disk: ' \
              'Resource disk12 not found.'
        with pytest.raises(GCECloudException) as error:
            self.cloud._get_disk('disk12')

        assert msg == str(error.value)

    @patch.object(GCECloud, '_get_subnet')
    def test_get_network_config(self, mock_get_subnet):
        subnet = 'projects/test/regions/us-west1/subnetworks/sub-123'
        net = 'projects/test/global/networks/network'

        mock_get_subnet.return_value = {
            'selfLink': subnet,
            'network': net
        }

        subnet_config = self.cloud._get_network_config('sub-123')

        assert subnet_config['network'] == net
        assert subnet_config['subnetwork'] == subnet

    def test_get_shielded_instance_config(self):
        si_config = self.cloud.get_shielded_instance_config()

        assert si_config['enableSecureBoot'] is False
        assert si_config['enableVtpm']
        assert si_config['enableIntegrityMonitoring']

    def test_get_instance_config(self):
        config = self.cloud.get_instance_config(
            'instance123',
            'n1-standard-1',
            [{}],
            'service-account-123@email.com',
            'image123',
            'secretkey',
            shielded_instance_config={'shielded': 'config'}
        )

        assert 'metadata' in config
        assert 'serviceAccounts' in config
        assert 'machineType' in config
        assert 'disks' in config
        assert 'networkInterfaces' in config
        assert 'name' in config
        assert 'shieldedInstanceConfig' in config

    @patch.object(GCECloud, '_wait_on_instance')
    @patch.object(GCECloud, '_wait_on_operation')
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
        mock_get_network.return_value = {
            'selfLink': 'projects/test/global/networks/net1'
        }
        mock_get_image.return_value = {
            'selfLink': 'projects/test/global/images/img-123'
        }
        mock_get_instance_type.return_value = {
            'selfLink': 'zones/us-west1-a/machineTypes/n1-standard-1'
        }
        mock_wait_on_operation.return_value = {}

        instances_obj = MagicMock()
        operation = MagicMock()
        operation.execute.return_value = {'name': 'operation123'}
        instances_obj.insert.return_value = operation
        self.cloud.compute_driver.instances.return_value = instances_obj

        self.cloud.region = 'us-west1-a'

        self.cloud._launch_instance()

        assert self.cloud.running_instance_id == 'test-instance'
        assert mock_wait_on_instance.call_count == 1

        # Exception on operation

        mock_wait_on_operation.return_value = {
            'error': {
                'errors': [{
                    'code': 'QUOTA_EXCEEDED',
                    'message': 'Too many cpus.'
                }]
            }
        }

        with pytest.raises(IpaRetryableError) as error:
            self.cloud._launch_instance()

        assert 'Failed to launch instance: Too many cpus.' == str(error.value)

        # Exception on API call

        mock_wait_on_operation.return_value = {}
        instances_obj.insert.side_effect = get_http_error(
            'Invalid instance type.',
            '412'
        )

        with pytest.raises(IpaRetryableError) as error:
            self.cloud._launch_instance()

        msg = 'Failed to launch instance: Invalid instance type.'
        assert msg == str(error.value)

    @patch.object(GCECloud, '_get_disk')
    @patch.object(GCECloud, '_get_instance')
    def test_gce_set_image_id(self, mock_get_instance, mock_get_disk):
        """Test gce cloud set image id method."""
        instance = {
            'disks': [{
                'deviceName': 'disk123',
                'boot': True,
                'source': 'https://www.googleapis.com/compute/v1/projects/'
                          'test/zones/us-west1-a/disks/disk123'
            }]
        }
        disk = {
            'sourceImage': 'projects/suse/global/images/opensuse-leap-15.0'
        }
        mock_get_instance.return_value = instance
        mock_get_disk.return_value = disk

        self.cloud._set_image_id()

        assert self.cloud.image_id == 'opensuse-leap-15.0'
        assert mock_get_instance.call_count == 1
        assert mock_get_disk.call_count == 1

    def test_gce_validate_region(self):
        """Test gce cloud set image id method."""
        zones_obj = MagicMock()
        operation = MagicMock()
        operation.execute.return_value = None
        zones_obj.get.return_value = operation
        self.cloud.compute_driver.zones.return_value = zones_obj

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
        mock_get_instance.return_value = {'status': 'RUNNING'}
        assert self.cloud._is_instance_running()
        assert mock_get_instance.call_count == 1

        mock_get_instance.return_value = {'status': 'TERMINATED'}
        assert not self.cloud._is_instance_running()

    @patch.object(GCECloud, '_get_instance')
    def test_gce_set_instance_ip(self, mock_get_instance):
        """Test gce cloud set instance ip method."""
        mock_get_instance.return_value = {
            'networkInterfaces': [{'some': 'data'}]
        }

        self.cloud.running_instance_id = 'test'

        with pytest.raises(GCECloudException) as error:
            self.cloud._set_instance_ip()

        assert str(error.value) == \
            'IP address for instance: test cannot be found.'
        assert mock_get_instance.call_count == 1

        mock_get_instance.return_value = {
            'networkInterfaces': [{'networkIP': '10.0.0.0'}]
        }
        self.cloud._set_instance_ip()

        assert self.cloud.instance_ip == '10.0.0.0'

    @patch.object(GCECloud, '_wait_on_instance')
    def test_gce_start_instance(self, mock_wait_on_instance):
        """Test gce start instance method."""
        mock_wait_on_instance.return_value = None

        instances_obj = MagicMock()
        operation = MagicMock()
        operation.execute.return_value = None
        instances_obj.start.return_value = operation
        self.cloud.compute_driver.instances.return_value = instances_obj

        self.cloud._start_instance()

        assert instances_obj.start.call_count == 1

    @patch.object(GCECloud, '_wait_on_instance')
    def test_gce_stop_instance(self, mock_wait_on_instance):
        """Test gce stop instance method."""
        mock_wait_on_instance.return_value = None

        instances_obj = MagicMock()
        operation = MagicMock()
        operation.execute.return_value = None
        instances_obj.stop.return_value = operation
        self.cloud.compute_driver.instances.return_value = instances_obj

        self.cloud._stop_instance()

        assert instances_obj.stop.call_count == 1

    def test_gce_terminate_instance(self):
        """Test gce terminate instance method."""
        instances_obj = MagicMock()
        operation = MagicMock()
        operation.execute.return_value = None
        instances_obj.delete.return_value = operation
        self.cloud.compute_driver.instances.return_value = instances_obj

        self.cloud._terminate_instance()
        assert instances_obj.delete.call_count == 1

    def test_gce_get_console_log(self):
        """Test gce get console log method."""
        instances_obj = MagicMock()
        operation = MagicMock()
        operation.execute.return_value = {'content': 'some output'}
        instances_obj.getSerialPortOutput.return_value = operation
        self.cloud.compute_driver.instances.return_value = instances_obj

        self.cloud.get_console_log()
        assert instances_obj.getSerialPortOutput.call_count == 1

    @patch('img_proof.ipa_gce.time')
    def test_wait_on_operation(self, mock_time):
        self.cloud.service_account_project = 'test_project'
        self.cloud.region = 'us-west1-a'

        mock_time.sleep.return_value = None
        mock_time.time.return_value = 10

        zone_ops_obj = MagicMock()
        operation = MagicMock()
        operation.execute.return_value = {'status': 'DONE'}
        zone_ops_obj.get.return_value = operation
        self.cloud.compute_driver.zoneOperations.return_value = zone_ops_obj

        result = self.cloud._wait_on_operation('operation213')
        assert result['status'] == 'DONE'
        assert zone_ops_obj.get.call_count == 1
