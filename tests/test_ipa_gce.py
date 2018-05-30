#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""Ipa GCE provider unit tests."""

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

import json
import pytest

from ipa.ipa_gce import GCEProvider
from ipa.ipa_exceptions import GCEProviderException

from unittest.mock import MagicMock, patch

from libcloud.common.google import ResourceNotFoundError


class TestGCEProvider(object):
    """Test GCE provider class."""

    def setup_method(self, method):
        """Set up kwargs dict."""
        self.kwargs = {
            'config': 'tests/data/config',
            'distro_name': 'SLES',
            'image_id': 'fakeimage',
            'no_default_test_dirs': True,
            'service_account_file': 'tests/gce/service-account.json',
            'ssh_private_key': 'tests/data/ida_test',
            'test_files': ['test_image']
        }

    def test_gce_exception_required_args(self):
        """Test an exception is raised if required args missing."""
        self.kwargs['service_account_file'] = None
        self.kwargs['ssh_private_key'] = None

        # Test service account file required
        with pytest.raises(GCEProviderException) as error:
            GCEProvider(**self.kwargs)

        assert str(error.value) == \
            'Service account file is required to connect to GCE.'

        self.kwargs['service_account_file'] = 'tests/gce/service-account.json'

        # Test ssh private key file required
        with pytest.raises(GCEProviderException) as error:
            GCEProvider(**self.kwargs)

        assert str(error.value) == \
            'SSH private key file is required to connect to instance.'

        self.kwargs['ssh_private_key'] = 'tests/data/ida_test'

    @patch.object(GCEProvider, '_get_ssh_public_key')
    @patch.object(GCEProvider, '_get_driver')
    def test_gce_get_service_account_info(self,
                                          mock_get_driver,
                                          mock_get_ssh_key):
        """Test get service account info method."""
        mock_get_driver.return_value = None
        mock_get_ssh_key.return_value = None
        provider = GCEProvider(**self.kwargs)

        provider._get_service_account_info()

        assert provider.service_account_email == \
            'test@test.iam.gserviceaccount.com'
        assert provider.service_account_project == 'test'

    @patch.object(GCEProvider, '_get_ssh_public_key')
    @patch('libcloud.compute.drivers.gce.GCENodeDriver')
    def test_gce_get_driver(self,
                            mock_node_driver,
                            mock_get_ssh_key):
        """Test gce get driver method."""
        driver = MagicMock()

        mock_node_driver.return_value = driver
        mock_get_ssh_key.return_value = None

        provider = GCEProvider(**self.kwargs)
        assert driver == provider.compute_driver

    @patch.object(GCEProvider, '_get_driver')
    def test_gce_get_disk_config(self,
                                 mock_get_driver):
        """Test gce get disk config method."""
        driver = MagicMock()
        mock_get_driver.return_value = driver

        disk_type = MagicMock()
        disk_type.extra = {'selfLink': 'disk_type_link'}
        driver.ex_get_disktype.return_value = disk_type

        image = MagicMock()
        image.extra = {'selfLink': 'image_link'}
        driver.ex_get_image.return_value = image

        provider = GCEProvider(**self.kwargs)
        provider.running_instance_id = 'instance123'
        config = provider._get_disk_config()

        expected_config = '[{"autoDelete": true, "boot": true, ' \
                          '"deviceName": "instance123", "initializeParams": ' \
                          '{"diskName": "instance123", "diskSizeGb": 10, ' \
                          '"diskType": "disk_type_link", ' \
                          '"sourceImage": "image_link"}, "mode": ' \
                          '"READ_WRITE", "type": "PERSISTENT"}]'

        assert json.dumps(config, sort_keys=True) == expected_config

    @patch.object(GCEProvider, '_get_driver')
    def test_get_disk_type_exception(self, mock_get_driver):
        driver = MagicMock()
        mock_get_driver.return_value = driver
        driver.ex_get_disktype.side_effect = Exception(
            'Invalid disk type'
        )

        provider = GCEProvider(**self.kwargs)

        with pytest.raises(Exception) as e:
            provider._get_disk_type()

        assert str(e.value) == \
            'Unable to locate disk device type: Invalid disk type.'

    @patch.object(GCEProvider, '_get_driver')
    def test_get_image_exception(self, mock_get_driver):
        driver = MagicMock()
        mock_get_driver.return_value = driver
        driver.ex_get_image.side_effect = Exception(
            'Invalid image type'
        )

        provider = GCEProvider(**self.kwargs)

        with pytest.raises(Exception) as e:
            provider._get_image()

        assert str(e.value) == \
            'Unable to locate image type: Invalid image type.'

    @patch.object(GCEProvider, '_get_ssh_public_key')
    @patch.object(GCEProvider, '_get_driver')
    def test_gce_get_instance(self,
                              mock_get_driver,
                              mock_get_ssh_key):
        """Test gce get instance method."""
        instance = MagicMock()
        driver = MagicMock()

        mock_get_driver.return_value = driver
        mock_get_ssh_key.return_value = None

        driver.ex_get_node.return_value = instance

        provider = GCEProvider(**self.kwargs)
        val = provider._get_instance()

        assert val == instance

        provider.running_instance_id = 'test-instance'
        driver.ex_get_node.side_effect = ResourceNotFoundError(
            'Broken',
            'test',
            'test'
        )

        with pytest.raises(GCEProviderException) as error:
            val = provider._get_instance()

        assert str(error.value) == "Instance with id: test-instance cannot" \
            " be found: 'Broken'"

    @patch.object(GCEProvider, '_get_driver')
    def test_gce_get_ssh_public_key(self, mock_get_driver):
        """Test GCE get instance method."""
        mock_get_driver.return_value = None

        provider = GCEProvider(**self.kwargs)
        assert provider.ssh_public_key

    @patch.object(GCEProvider, '_get_driver')
    def test_gce_get_subnet(self, mock_get_driver):
        """Test GCE get subnetwork method."""
        subnetwork = MagicMock()
        driver = MagicMock()
        driver.ex_get_subnetwork.return_value = subnetwork
        mock_get_driver.return_value = driver

        provider = GCEProvider(**self.kwargs)
        provider.region = 'us-west-1a'
        result = provider._get_subnet('test-subnet')

        assert result == subnetwork

    @patch.object(GCEProvider, '_get_driver')
    def test_gce_get_subnet_exception(self, mock_get_driver):
        """Test GCE get subnetwork method."""
        driver = MagicMock()
        driver.ex_get_subnetwork.side_effect = Exception('Cannot find subnet!')
        mock_get_driver.return_value = driver

        provider = GCEProvider(**self.kwargs)
        provider.region = 'us-west-1a'

        msg = 'GCE subnet: test-subnet not found.'
        with pytest.raises(GCEProviderException) as error:
            provider._get_subnet('test-subnet')

        assert msg == str(error.value)

    @patch.object(GCEProvider, '_get_disk_config')
    @patch.object(GCEProvider, '_get_subnet')
    @patch('ipa.ipa_utils.generate_instance_name')
    @patch.object(GCEProvider, '_get_driver')
    def test_gce_launch_instance(self,
                                 mock_get_driver,
                                 mock_generate_instance_name,
                                 mock_get_subnet,
                                 mock_get_disk_config):
        """Test GCE launch instance method."""
        driver = MagicMock()
        instance = MagicMock()
        driver.create_node.return_value = instance
        driver.wait_until_running.return_value = None

        mock_get_driver.return_value = driver
        mock_generate_instance_name.return_value = 'test-instance'

        mock_get_disk_config.return_value = [{
            'autoDelete': True,
            'boot': True,
            'type': 'PERSISTENT',
            'mode': 'READ_WRITE',
            'deviceName': 'test-instance',
            'initializeParams': {
                'diskName': 'test-instance',
                'diskSizeGb': 10,
                'diskType': 'disk_type',
                'sourceImage': 'source_image'
            }
        }]

        provider = GCEProvider(**self.kwargs)
        provider.region = None

        with pytest.raises(GCEProviderException) as error:
            provider._launch_instance()

        assert str(error.value) == \
            'Zone is required to launch a new GCE instance. ' \
            'Example: us-west1-a'

        provider.region = 'us-west1-a'
        provider.subnet_id = 'test-subnet'

        subnet = MagicMock()
        network = MagicMock()
        subnet.network = network
        mock_get_subnet.return_value = subnet

        provider._launch_instance()

        assert provider.running_instance_id == 'test-instance'

    @patch.object(GCEProvider, '_get_ssh_public_key')
    @patch.object(GCEProvider, '_get_driver')
    @patch.object(GCEProvider, '_get_instance')
    def test_gce_set_image_id(self,
                              mock_get_instance,
                              mock_get_driver,
                              mock_get_ssh_key):
        """Test ec2 provider set image id method."""
        instance = MagicMock()
        instance.image = 'test-image'
        mock_get_instance.return_value = instance
        mock_get_driver.return_value = None
        mock_get_ssh_key.return_value = None

        provider = GCEProvider(**self.kwargs)
        provider._set_image_id()

        assert provider.image_id == instance.image
        assert mock_get_instance.call_count == 1
