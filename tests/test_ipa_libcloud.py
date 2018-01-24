#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""Ipa libcloud provider unit tests."""

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

from ipa.ipa_exceptions import LibcloudProviderException
from ipa.ipa_libcloud import LibcloudProvider

from unittest.mock import MagicMock, patch

args = ['EC2']


class TestLibcloudProvider(object):
    """Test libcloud provider class."""

    def setup_method(self, method):
        """Set up kwargs dict."""
        self.kwargs = {
            'config': 'tests/data/config',
            'distro_name': 'SLES',
            'history_log': 'tests/data/results/.history',
            'image_id': 'fakeimage',
            'no_default_test_dirs': True,
            'results_dir': 'tests/data/results',
            'test_dirs': 'tests/data/tests',
            'test_files': ['test_image']
        }

    @patch.object(LibcloudProvider, '_get_instance')
    def test_libcloud_get_instance_state(self, mock_get_instance):
        """Test libcloud get instance method."""
        instance = MagicMock()
        instance.state = 'running'

        mock_get_instance.return_value = instance

        provider = LibcloudProvider(*args, **self.kwargs)
        val = provider._get_instance_state()

        assert val == 'running'
        assert mock_get_instance.call_count == 1

    @patch.object(LibcloudProvider, '_get_instance_state')
    def test_libcloud_is_instance_running(self, mock_get_instance_state):
        """Test libcloud provider is instance runnning method."""
        mock_get_instance_state.return_value = 'running'

        provider = LibcloudProvider(*args, **self.kwargs)
        assert provider._is_instance_running()
        assert mock_get_instance_state.call_count == 1

        mock_get_instance_state.return_value = 'stopped'
        mock_get_instance_state.reset_mock()

        provider = LibcloudProvider(*args, **self.kwargs)
        assert not provider._is_instance_running()
        assert mock_get_instance_state.call_count == 1

    @patch.object(LibcloudProvider, '_get_instance')
    def test_libcloud_set_instance_ip(self, mock_get_instance):
        """Test libcloud provider set instance ip method."""
        instance = MagicMock()
        instance.public_ips = []
        instance.private_ips = []

        mock_get_instance.return_value = instance

        provider = LibcloudProvider(*args, **self.kwargs)
        provider.running_instance_id = 'test'

        with pytest.raises(LibcloudProviderException) as error:
            provider._set_instance_ip()

        assert str(error.value) == \
            'IP address for instance: test cannot be found.'
        assert mock_get_instance.call_count == 1

        mock_get_instance.reset_mock()

        instance.public_ips = ['127.0.0.1']
        provider._set_instance_ip()

        assert provider.instance_ip == '127.0.0.1'
        assert mock_get_instance.call_count == 1

    @patch.object(LibcloudProvider, '_get_instance')
    def test_libcloud_start_instance(self, mock_get_instance):
        """Test libcloud start instance method."""
        instance = MagicMock()
        mock_get_instance.return_value = instance

        provider = LibcloudProvider(*args, **self.kwargs)

        driver = MagicMock()
        driver.ex_start_node.return_value = None
        driver.wait_until_running.return_value = None
        provider.compute_driver = driver

        provider._start_instance()

        assert mock_get_instance.call_count == 1
        assert driver.ex_start_node.call_count == 1
        assert driver.wait_until_running.call_count == 1

    @patch.object(LibcloudProvider, '_wait_on_instance')
    @patch.object(LibcloudProvider, '_get_instance')
    def test_libcloud_stop_instance(self,
                                    mock_get_instance,
                                    mock_wait_on_instance):
        """Test libcloud stop instance method."""
        instance = MagicMock()
        mock_get_instance.return_value = instance

        mock_wait_on_instance.return_value = None

        provider = LibcloudProvider(*args, **self.kwargs)

        driver = MagicMock()
        driver.ex_stop_node.return_value = None
        provider.compute_driver = driver

        provider._stop_instance()

        assert mock_get_instance.call_count == 1
        assert driver.ex_stop_node.call_count == 1

    @patch.object(LibcloudProvider, '_get_instance')
    def test_libcloud_terminate_instance(self, mock_get_instance):
        """Test libcloud terminate instance method."""
        instance = MagicMock()
        instance.destroy.return_value = None
        mock_get_instance.return_value = instance

        provider = LibcloudProvider(*args, **self.kwargs)

        driver = MagicMock()
        provider.compute_driver = driver
        provider._terminate_instance()

        assert mock_get_instance.call_count == 1
        assert instance.destroy.call_count == 1
