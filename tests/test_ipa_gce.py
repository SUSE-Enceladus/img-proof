#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""Ipa GCE cloud unit tests."""

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

import pytest

from ipa.ipa_gce import GCECloud
from ipa.ipa_exceptions import GCECloudException

from unittest.mock import MagicMock, patch

from libcloud.common.google import ResourceNotFoundError


class TestGCECloud(object):
    """Test GCE cloud class."""

    def setup_method(self, method):
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

    @patch.object(GCECloud, '_validate_region')
    @patch.object(GCECloud, '_get_ssh_public_key')
    @patch.object(GCECloud, '_get_driver')
    def test_gce_get_service_account_info(self,
                                          mock_get_driver,
                                          mock_get_ssh_key,
                                          mock_validate_region):
        """Test get service account info method."""
        mock_get_driver.return_value = None
        mock_get_ssh_key.return_value = None
        cloud = GCECloud(**self.kwargs)

        cloud._get_service_account_info()

        assert cloud.service_account_email == \
            'test@test.iam.gserviceaccount.com'
        assert cloud.service_account_project == 'test'

    @patch.object(GCECloud, '_validate_region')
    @patch.object(GCECloud, '_get_ssh_public_key')
    @patch.object(GCECloud, '_get_driver')
    def test_gce_get_service_account_info_invalid(
        self,
        mock_get_driver,
        mock_get_ssh_key,
        mock_validate_region
    ):
        """Test get service account info method."""
        mock_get_driver.return_value = None
        mock_get_ssh_key.return_value = None
        cloud = GCECloud(**self.kwargs)

        cloud.service_account_file = \
            'tests/gce/invalid-service-account.json'

        with pytest.raises(GCECloudException) as error:
            cloud._get_service_account_info()

        msg = 'Service account JSON file is invalid for GCE. ' \
            'client_email key is expected. See getting started ' \
            'docs for information on GCE configuration.'
        assert str(error.value) == msg

    @patch.object(GCECloud, '_validate_region')
    @patch.object(GCECloud, '_get_ssh_public_key')
    @patch('libcloud.compute.drivers.gce.GCENodeDriver')
    def test_gce_get_driver(self,
                            mock_node_driver,
                            mock_get_ssh_key,
                            mock_validate_region):
        """Test gce get driver method."""
        driver = MagicMock()

        mock_node_driver.return_value = driver
        mock_get_ssh_key.return_value = None

        cloud = GCECloud(**self.kwargs)
        assert driver == cloud.compute_driver

    @patch.object(GCECloud, '_validate_region')
    @patch.object(GCECloud, '_get_ssh_public_key')
    @patch.object(GCECloud, '_get_driver')
    def test_gce_get_instance(self,
                              mock_get_driver,
                              mock_get_ssh_key,
                              mock_validate_region):
        """Test gce get instance method."""
        instance = MagicMock()
        driver = MagicMock()

        mock_get_driver.return_value = driver
        mock_get_ssh_key.return_value = None

        driver.ex_get_node.return_value = instance

        cloud = GCECloud(**self.kwargs)
        val = cloud._get_instance()

        assert val == instance

        cloud.running_instance_id = 'test-instance'
        driver.ex_get_node.side_effect = ResourceNotFoundError(
            'Broken',
            'test',
            'test'
        )

        with pytest.raises(GCECloudException) as error:
            val = cloud._get_instance()

        assert str(error.value) == "Instance with id: test-instance cannot" \
            " be found: 'Broken'"

    @patch.object(GCECloud, '_validate_region')
    @patch.object(GCECloud, '_get_driver')
    def test_gce_get_ssh_public_key(
        self,
        mock_get_driver,
        mock_validate_region
    ):
        """Test GCE get instance method."""
        mock_get_driver.return_value = None

        cloud = GCECloud(**self.kwargs)
        assert cloud.ssh_public_key

    @patch.object(GCECloud, '_validate_region')
    @patch.object(GCECloud, '_get_driver')
    def test_gce_get_subnet(
        self,
        mock_get_driver,
        mock_validate_region
    ):
        """Test GCE get subnetwork method."""
        subnetwork = MagicMock()
        driver = MagicMock()
        driver.ex_get_subnetwork.return_value = subnetwork
        mock_get_driver.return_value = driver

        cloud = GCECloud(**self.kwargs)
        cloud.region = 'us-west-1a'
        result = cloud._get_subnet('test-subnet')

        assert result == subnetwork

    @patch.object(GCECloud, '_validate_region')
    @patch.object(GCECloud, '_get_driver')
    def test_gce_get_subnet_exception(
        self,
        mock_get_driver,
        mock_validate_region
    ):
        """Test GCE get subnetwork method."""
        driver = MagicMock()
        driver.ex_get_subnetwork.side_effect = Exception('Cannot find subnet!')
        mock_get_driver.return_value = driver

        cloud = GCECloud(**self.kwargs)
        cloud.region = 'us-west-1a'

        msg = 'GCE subnet: test-subnet not found.'
        with pytest.raises(GCECloudException) as error:
            cloud._get_subnet('test-subnet')

        assert msg == str(error.value)

    @patch.object(GCECloud, '_validate_region')
    @patch.object(GCECloud, '_get_subnet')
    @patch('ipa.ipa_utils.generate_instance_name')
    @patch.object(GCECloud, '_get_driver')
    def test_gce_launch_instance(self,
                                 mock_get_driver,
                                 mock_generate_instance_name,
                                 mock_get_subnet,
                                 mock_validate_region):
        """Test GCE launch instance method."""
        driver = MagicMock()
        instance = MagicMock()
        driver.create_node.return_value = instance
        driver.wait_until_running.return_value = None

        mock_get_driver.return_value = driver
        mock_generate_instance_name.return_value = 'test-instance'

        cloud = GCECloud(**self.kwargs)

        cloud.region = 'us-west1-a'
        cloud.subnet_id = 'test-subnet'

        subnet = MagicMock()
        network = MagicMock()
        subnet.network = network
        mock_get_subnet.return_value = subnet

        cloud._launch_instance()

        assert cloud.running_instance_id == 'test-instance'

    @patch.object(GCECloud, '_validate_region')
    @patch.object(GCECloud, '_get_ssh_public_key')
    @patch.object(GCECloud, '_get_driver')
    @patch.object(GCECloud, '_get_instance')
    def test_gce_set_image_id(self,
                              mock_get_instance,
                              mock_get_driver,
                              mock_get_ssh_key,
                              mock_validate_region):
        """Test gce cloud set image id method."""
        instance = MagicMock()
        instance.image = 'test-image'
        mock_get_instance.return_value = instance
        mock_get_driver.return_value = None
        mock_get_ssh_key.return_value = None

        cloud = GCECloud(**self.kwargs)
        cloud._set_image_id()

        assert cloud.image_id == instance.image
        assert mock_get_instance.call_count == 1

    @patch.object(GCECloud, '_get_driver')
    def test_gce_validate_region(self, mock_get_driver):
        """Test gce cloud set image id method."""
        driver = MagicMock()
        driver.ex_get_zone.return_value = None
        mock_get_driver.return_value = driver

        with pytest.raises(GCECloudException) as error:
            GCECloud(**self.kwargs)

        assert str(error.value) == \
            'Zone is required for GCE cloud framework: Example: us-west1-a'

        self.kwargs['region'] = 'fake'

        with pytest.raises(GCECloudException) as error:
            GCECloud(**self.kwargs)

        driver.ex_get_zone.assert_called_once_with('fake')

        assert str(error.value) == \
            'fake is not a valid GCE zone. Example: us-west1-a'

    @patch.object(GCECloud, '_validate_region')
    @patch.object(GCECloud, '_get_driver')
    @patch.object(GCECloud, '_get_ssh_public_key')
    @patch.object(GCECloud, '_get_instance')
    def test_gce_get_instance_state(
        self,
        mock_get_instance,
        mock_get_ssh_key,
        mock_get_driver,
        mock_validate_region
    ):
        """Test gce get instance method."""
        driver = MagicMock()
        mock_get_driver.return_value = driver
        mock_get_ssh_key.return_value = None

        instance = MagicMock()
        instance.state = 'running'

        mock_get_instance.return_value = instance

        cloud = GCECloud(**self.kwargs)
        val = cloud._get_instance_state()

        assert val == 'running'
        assert mock_get_instance.call_count == 1

    @patch.object(GCECloud, '_validate_region')
    @patch.object(GCECloud, '_get_driver')
    @patch.object(GCECloud, '_get_ssh_public_key')
    @patch.object(GCECloud, '_get_instance_state')
    def test_gce_is_instance_running(
        self,
        mock_get_instance_state,
        mock_get_ssh_key,
        mock_get_driver,
        mock_validate_region
    ):
        """Test gce cloud is instance runnning method."""
        driver = MagicMock()
        mock_get_driver.return_value = driver
        mock_get_ssh_key.return_value = None

        mock_get_instance_state.return_value = 'running'

        cloud = GCECloud(**self.kwargs)
        assert cloud._is_instance_running()
        assert mock_get_instance_state.call_count == 1

        mock_get_instance_state.return_value = 'stopped'
        mock_get_instance_state.reset_mock()

        cloud = GCECloud(**self.kwargs)
        assert not cloud._is_instance_running()
        assert mock_get_instance_state.call_count == 1

    @patch.object(GCECloud, '_validate_region')
    @patch.object(GCECloud, '_get_driver')
    @patch.object(GCECloud, '_get_ssh_public_key')
    @patch.object(GCECloud, '_get_instance')
    def test_gce_set_instance_ip(
        self,
        mock_get_instance,
        mock_get_ssh_key,
        mock_get_driver,
        mock_validate_region
    ):
        """Test gce cloud set instance ip method."""
        driver = MagicMock()
        mock_get_driver.return_value = driver
        mock_get_ssh_key.return_value = None

        instance = MagicMock()
        instance.public_ips = []
        instance.private_ips = []

        mock_get_instance.return_value = instance

        cloud = GCECloud(**self.kwargs)
        cloud.running_instance_id = 'test'

        with pytest.raises(GCECloudException) as error:
            cloud._set_instance_ip()

        assert str(error.value) == \
            'IP address for instance: test cannot be found.'
        assert mock_get_instance.call_count == 1

        mock_get_instance.reset_mock()

        instance.public_ips = ['127.0.0.1']
        cloud._set_instance_ip()

        assert cloud.instance_ip == '127.0.0.1'
        assert mock_get_instance.call_count == 1

    @patch.object(GCECloud, '_validate_region')
    @patch.object(GCECloud, '_get_driver')
    @patch.object(GCECloud, '_get_ssh_public_key')
    @patch.object(GCECloud, '_get_instance')
    def test_gce_start_instance(
        self,
        mock_get_instance,
        mock_get_ssh_key,
        mock_get_driver,
        mock_validate_region
    ):
        """Test gce start instance method."""
        driver = MagicMock()
        mock_get_driver.return_value = driver
        mock_get_ssh_key.return_value = None

        instance = MagicMock()
        mock_get_instance.return_value = instance

        cloud = GCECloud(**self.kwargs)

        driver = MagicMock()
        driver.ex_start_node.return_value = None
        driver.wait_until_running.return_value = None
        cloud.compute_driver = driver

        cloud._start_instance()

        assert mock_get_instance.call_count == 1
        assert driver.ex_start_node.call_count == 1
        assert driver.wait_until_running.call_count == 1

    @patch.object(GCECloud, '_validate_region')
    @patch.object(GCECloud, '_get_driver')
    @patch.object(GCECloud, '_wait_on_instance')
    @patch.object(GCECloud, '_get_ssh_public_key')
    @patch.object(GCECloud, '_get_instance')
    def test_gce_stop_instance(
        self,
        mock_get_instance,
        mock_get_ssh_key,
        mock_wait_on_instance,
        mock_get_driver,
        mock_validate_region
    ):
        """Test gce stop instance method."""
        driver = MagicMock()
        mock_get_driver.return_value = driver
        mock_get_ssh_key.return_value = None

        instance = MagicMock()
        mock_get_instance.return_value = instance

        mock_wait_on_instance.return_value = None

        cloud = GCECloud(**self.kwargs)

        driver = MagicMock()
        driver.ex_stop_node.return_value = None
        cloud.compute_driver = driver

        cloud._stop_instance()

        assert mock_get_instance.call_count == 1
        assert driver.ex_stop_node.call_count == 1

    @patch.object(GCECloud, '_validate_region')
    @patch.object(GCECloud, '_get_driver')
    @patch.object(GCECloud, '_get_ssh_public_key')
    @patch.object(GCECloud, '_get_instance')
    def test_gce_terminate_instance(
        self,
        mock_get_instance,
        mock_get_ssh_key,
        mock_get_driver,
        mock_validate_region
    ):
        """Test gce terminate instance method."""
        driver = MagicMock()
        mock_get_driver.return_value = driver
        mock_get_ssh_key.return_value = None

        instance = MagicMock()
        instance.destroy.return_value = None
        mock_get_instance.return_value = instance

        cloud = GCECloud(**self.kwargs)

        driver = MagicMock()
        cloud.compute_driver = driver
        cloud._terminate_instance()

        assert mock_get_instance.call_count == 1
        assert instance.destroy.call_count == 1
