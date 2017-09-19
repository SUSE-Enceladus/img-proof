#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""Ipa ec2 provider unit tests."""

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

import boto3
import pytest

from ipa.ipa_ec2 import EC2Provider
from ipa.ipa_exceptions import EC2ProviderException

from unittest.mock import MagicMock, patch


class TestEC2Provider(object):
    """Test EC2 provider class."""

    def setup_method(self, method):
        """Set up kwargs dict."""
        self.kwargs = {
            'account_name': 'bob',
            'config': 'tests/data/config',
            'distro_name': 'SLES',
            'image_id': 'fakeimage',
            'no_default_test_dirs': True,
            'provider_config': 'tests/ec2/.ec2utils.conf',
            'test_files': ['test_image']
        }

    def test_ec2_exception_required_args(self):
        """Test an exception is raised if required args missing."""
        self.kwargs['account_name'] = None
        msg = 'Account required for config file: %s' \
            % self.kwargs['provider_config']

        # Test account required
        with pytest.raises(EC2ProviderException) as error:
            EC2Provider(**self.kwargs)

        assert str(error.value) == msg

        self.kwargs['config'] = 'tests/data/config.noregion'
        self.kwargs['account_name'] = 'bob'
        msg = 'Region is required to connect to EC2.'

        # Test region required
        with pytest.raises(EC2ProviderException) as error:
            EC2Provider(**self.kwargs)

        assert str(error.value) == msg

        self.kwargs['provider_config'] = 'tests/ec2/.ec2utils.conf.nokey'
        self.kwargs['config'] = 'tests/data/config'
        msg = 'SSH private key file is required to connect to instance.'

        # Test ssh private key file required
        with pytest.raises(EC2ProviderException) as error:
            EC2Provider(**self.kwargs)

        assert str(error.value) == msg
        self.kwargs['provider_config'] = 'tests/ec2/.ec2utils.conf'

    @patch.object(boto3, 'resource')
    def test_ec2_bad_connection(self, mock_boto3):
        """Test an exception is raised if boto3 unable to connect."""
        mock_boto3.side_effect = Exception('ERROR!')

        provider = EC2Provider(**self.kwargs)
        msg = 'Could not connect to region: %s' % provider.region

        # Test ssh private key file required
        with pytest.raises(EC2ProviderException) as error:
            provider._connect()

        assert str(error.value) == msg
        assert mock_boto3.call_count > 0

    @patch.object(EC2Provider, '_connect')
    def test_ec2_get_instance(self, mock_connect):
        """Test get instance method."""
        instance = MagicMock()
        resource = MagicMock()
        resource.Instance.return_value = instance
        mock_connect.return_value = resource

        provider = EC2Provider(**self.kwargs)
        val = provider._get_instance()
        assert val == instance
        assert mock_connect.call_count == 1

    @patch.object(EC2Provider, '_get_instance')
    def test_ec2_get_instance_state(self, mock_get_instance):
        """Test an exception is raised if boto3 unable to connect."""
        instance = MagicMock()
        instance.state = {'Name': 'ReadyRole'}
        mock_get_instance.return_value = instance

        provider = EC2Provider(**self.kwargs)
        val = provider._get_instance_state()
        assert val == 'ReadyRole'
        assert mock_get_instance.call_count == 1

        instance.state = {}
        mock_get_instance.reset_mock()
        msg = 'Instance with id: %s, cannot be found.' \
            % provider.running_instance_id

        # Test exception raised if instance state not found
        with pytest.raises(EC2ProviderException) as error:
            provider._get_instance_state()

        assert str(error.value) == msg
        assert mock_get_instance.call_count == 1

    @patch.object(EC2Provider, '_get_instance_state')
    def test_ec2_is_instance_running(self, mock_get_instance_state):
        """Test ec2 provider is instance runnning method."""
        mock_get_instance_state.return_value = 'running'

        provider = EC2Provider(**self.kwargs)
        assert provider._is_instance_running()
        assert mock_get_instance_state.call_count == 1

        mock_get_instance_state.return_value = 'stopped'
        mock_get_instance_state.reset_mock()

        provider = EC2Provider(**self.kwargs)
        assert not provider._is_instance_running()
        assert mock_get_instance_state.call_count == 1

    def test_ec2_launch_no_key_name(self):
        """Test ec2 provider raises exception if no ssh key name method."""
        provider = EC2Provider(**self.kwargs)
        provider.ssh_key_name = None
        msg = 'SSH Key Name is required to launch an EC2 instance.'

        with pytest.raises(EC2ProviderException) as error:
            provider._launch_instance()

        assert str(error.value) == msg

    @patch.object(EC2Provider, '_get_instance')
    def test_ec2_set_image_id(self, mock_get_instance):
        """Test ec2 provider set image id method."""
        instance = MagicMock()
        instance.image_id = 'ami-123456'
        mock_get_instance.return_value = instance

        provider = EC2Provider(**self.kwargs)
        provider._set_image_id()

        assert provider.image_id == instance.image_id
        assert mock_get_instance.call_count == 1

    @patch.object(EC2Provider, '_get_instance')
    def test_ec2_set_instance_ip(self, mock_get_instance):
        """Test ec2 provider set image id method."""
        instance = MagicMock()
        instance.public_ip_address = None
        instance.network_interfaces = []
        mock_get_instance.return_value = instance

        provider = EC2Provider(**self.kwargs)
        msg = 'IP address for instance cannot be found.'

        with pytest.raises(EC2ProviderException) as error:
            provider._set_instance_ip()

        assert str(error.value) == msg
        assert mock_get_instance.call_count == 1
        mock_get_instance.reset_mock()

        network_interface = MagicMock()
        network_interface.ipv6_addresses = ['127.0.0.1']
        instance.network_interfaces = [network_interface]

        provider._set_instance_ip()
        assert provider.instance_ip == '127.0.0.1'
        assert mock_get_instance.call_count == 1
        mock_get_instance.reset_mock()

        instance.public_ip_address = '127.0.0.2'

        provider._set_instance_ip()
        assert provider.instance_ip == '127.0.0.2'
        assert mock_get_instance.call_count == 1

    @patch.object(EC2Provider, '_get_instance')
    def test_ec2_start_instance(self, mock_get_instance):
        """Test ec2 start instance method."""
        instance = MagicMock()
        instance.start.return_value = None
        instance.wait_until_running.return_value = None
        mock_get_instance.return_value = instance

        provider = EC2Provider(**self.kwargs)
        provider._start_instance()
        assert mock_get_instance.call_count == 1

    @patch.object(EC2Provider, '_get_instance')
    def test_ec2_stop_instance(self, mock_get_instance):
        """Test ec2 stop instance method."""
        instance = MagicMock()
        instance.stop.return_value = None
        instance.wait_until_stopped.return_value = None
        mock_get_instance.return_value = instance

        provider = EC2Provider(**self.kwargs)
        provider._stop_instance()
        assert mock_get_instance.call_count == 1

    @patch.object(EC2Provider, '_get_instance')
    def test_ec2_terminate_instance(self, mock_get_instance):
        """Test ec2 terminate instance method."""
        instance = MagicMock()
        instance.terminate.return_value = None
        mock_get_instance.return_value = instance

        provider = EC2Provider(**self.kwargs)
        provider._terminate_instance()
        assert mock_get_instance.call_count == 1
