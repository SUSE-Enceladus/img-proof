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
        assert driver == provider.gce_driver

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

    @patch.object(GCEProvider, '_get_ssh_public_key')
    @patch.object(GCEProvider, '_get_driver')
    @patch.object(GCEProvider, '_get_instance')
    def test_gce_get_instance_state(self,
                                    mock_get_instance,
                                    mock_get_driver,
                                    mock_get_ssh_key):
        """Test GCE get instance method."""
        instance = MagicMock()
        instance.state = 'running'

        mock_get_instance.return_value = instance
        mock_get_driver.return_value = None
        mock_get_ssh_key.return_value = None

        provider = GCEProvider(**self.kwargs)
        val = provider._get_instance_state()
        assert val == 'running'
        assert mock_get_instance.call_count == 1

    @patch.object(GCEProvider, '_get_driver')
    def test_gce_get_ssh_public_key(self, mock_get_driver):
        """Test GCE get instance method."""
        mock_get_driver.return_value = None

        provider = GCEProvider(**self.kwargs)
        assert provider.ssh_public_key

    @patch.object(GCEProvider, '_get_ssh_public_key')
    @patch.object(GCEProvider, '_get_driver')
    @patch.object(GCEProvider, '_get_instance_state')
    def test_gce_is_instance_running(self,
                                     mock_get_instance_state,
                                     mock_get_driver,
                                     mock_get_ssh_key):
        """Test gce provider is instance runnning method."""
        mock_get_instance_state.return_value = 'running'
        mock_get_driver.return_value = None
        mock_get_ssh_key.return_value = None

        provider = GCEProvider(**self.kwargs)
        assert provider._is_instance_running()
        assert mock_get_instance_state.call_count == 1

        mock_get_instance_state.return_value = 'stopped'
        mock_get_instance_state.reset_mock()

        provider = GCEProvider(**self.kwargs)
        assert not provider._is_instance_running()
        assert mock_get_instance_state.call_count == 1

    @patch('ipa.ipa_utils.generate_instance_name')
    @patch.object(GCEProvider, '_get_driver')
    def test_gce_launch_instance(self,
                                 mock_get_driver,
                                 mock_generate_instance_name):
        """Test GCE launch instance method."""
        driver = MagicMock()
        instance = MagicMock()
        driver.create_node.return_value = instance
        driver.wait_until_running.return_value = None

        mock_get_driver.return_value = driver
        mock_generate_instance_name.return_value = 'test-instance'

        provider = GCEProvider(**self.kwargs)
        provider.region = None

        with pytest.raises(GCEProviderException) as error:
            provider._launch_instance()

        assert str(error.value) == \
            'Zone (region) is required to launch a new GCE instance.'

        provider.region = 'us-west1-a'
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

    @patch.object(GCEProvider, '_get_ssh_public_key')
    @patch.object(GCEProvider, '_get_driver')
    @patch.object(GCEProvider, '_get_instance')
    def test_gce_set_instance_ip(self,
                                 mock_get_instance,
                                 mock_get_driver,
                                 mock_get_ssh_key):
        """Test gce provider set image id method."""
        instance = MagicMock()
        instance.public_ips = []

        mock_get_instance.return_value = instance
        mock_get_driver.return_value = None
        mock_get_ssh_key.return_value = None

        provider = GCEProvider(**self.kwargs)
        provider.running_instance_id = 'test'

        with pytest.raises(GCEProviderException) as error:
            provider._set_instance_ip()

        assert str(error.value) == \
            'IP address for instance: test cannot be found.'
        assert mock_get_instance.call_count == 1
        mock_get_instance.reset_mock()

        instance.public_ips = ['127.0.0.1']
        provider._set_instance_ip()

        assert provider.instance_ip == '127.0.0.1'
        assert mock_get_instance.call_count == 1

    @patch.object(GCEProvider, '_get_ssh_public_key')
    @patch.object(GCEProvider, '_get_driver')
    @patch.object(GCEProvider, '_get_instance')
    def test_gce_start_instance(self,
                                mock_get_instance,
                                mock_get_driver,
                                mock_get_ssh_key):
        """Test gce start instance method."""
        instance = MagicMock()
        driver = MagicMock()

        mock_get_instance.return_value = instance
        mock_get_driver.return_value = driver
        mock_get_ssh_key.return_value = None

        driver.ex_start_node.return_value = None
        driver.wait_until_running.return_value = None

        provider = GCEProvider(**self.kwargs)
        provider._start_instance()
        assert mock_get_instance.call_count == 1

    @patch.object(GCEProvider, '_get_ssh_public_key')
    @patch.object(GCEProvider, '_get_driver')
    @patch.object(GCEProvider, '_get_instance')
    def test_gce_stop_instance(self,
                               mock_get_instance,
                               mock_get_driver,
                               mock_get_ssh_key):
        """Test gce stop instance method."""
        instance = MagicMock()
        driver = MagicMock()

        mock_get_instance.return_value = instance
        mock_get_driver.return_value = driver
        mock_get_ssh_key.return_value = None

        driver.ex_stop_node.return_value = None

        provider = GCEProvider(**self.kwargs)
        provider._stop_instance()
        assert mock_get_instance.call_count == 1

    @patch.object(GCEProvider, '_get_ssh_public_key')
    @patch.object(GCEProvider, '_get_driver')
    @patch.object(GCEProvider, '_get_instance')
    def test_gce_terminate_instance(self,
                                    mock_get_instance,
                                    mock_get_driver,
                                    mock_get_ssh_key):
        """Test gce terminate instance method."""
        instance = MagicMock()
        instance.terminate.return_value = None

        mock_get_instance.return_value = instance
        mock_get_driver.return_value = None
        mock_get_ssh_key.return_value = None

        provider = GCEProvider(**self.kwargs)
        provider._terminate_instance()
        assert mock_get_instance.call_count == 1
