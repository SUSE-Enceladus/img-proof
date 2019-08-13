#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""img_proof ec2 provider unit tests."""

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

import boto3
import pytest

from img_proof.ipa_ec2 import EC2Cloud
from img_proof.ipa_exceptions import EC2CloudException

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
            'cloud_config': 'tests/ec2/.ec2utils.conf',
            'test_files': ['test_image'],
            'ssh_key_name': 'test-key'
        }

    def test_ec2_exception_required_args(self):
        """Test an exception is raised if required args missing."""
        self.kwargs['config'] = 'tests/data/config.noregion'
        msg = 'Region is required to connect to EC2.'

        # Test region required
        with pytest.raises(EC2CloudException) as error:
            EC2Cloud(**self.kwargs)

        assert str(error.value) == msg

        self.kwargs['cloud_config'] = 'tests/ec2/.ec2utils.conf.nokey'
        self.kwargs['config'] = 'tests/data/config'
        msg = 'SSH private key file is required to connect to instance.'

        # Test ssh private key file required
        with pytest.raises(EC2CloudException) as error:
            EC2Cloud(**self.kwargs)

        assert str(error.value) == msg
        self.kwargs['cloud_config'] = 'tests/ec2/.ec2utils.conf'

    @patch.object(boto3, 'resource')
    def test_ec2_bad_connection(self, mock_boto3):
        """Test an exception is raised if boto3 unable to connect."""
        mock_boto3.side_effect = Exception('ERROR!')

        provider = EC2Cloud(**self.kwargs)
        msg = 'Could not connect to region: %s' % provider.region

        # Test ssh private key file required
        with pytest.raises(EC2CloudException) as error:
            provider._connect()

        assert str(error.value) == msg
        assert mock_boto3.call_count > 0

    @patch.object(EC2Cloud, '_connect')
    def test_ec2_get_instance(self, mock_connect):
        """Test get instance method."""
        instance = MagicMock()
        resource = MagicMock()
        resource.Instance.return_value = instance
        mock_connect.return_value = resource

        provider = EC2Cloud(**self.kwargs)
        val = provider._get_instance()
        assert val == instance
        assert mock_connect.call_count == 1

    @patch.object(EC2Cloud, '_connect')
    def test_ec2_get_instance_error(self, mock_connect):
        """Test get instance method error."""
        resource = MagicMock()
        resource.Instance.side_effect = Exception('Error!')
        mock_connect.return_value = resource

        provider = EC2Cloud(**self.kwargs)
        provider.running_instance_id = 'i-123456789'

        with pytest.raises(EC2CloudException) as error:
            provider._get_instance()

        msg = 'Instance with ID: i-123456789 not found.'
        assert str(error.value) == msg

    @patch.object(EC2Cloud, '_get_instance')
    def test_ec2_get_instance_state(self, mock_get_instance):
        """Test an exception is raised if boto3 unable to connect."""
        instance = MagicMock()
        instance.state = {'Name': 'ReadyRole'}
        mock_get_instance.return_value = instance

        provider = EC2Cloud(**self.kwargs)
        val = provider._get_instance_state()
        assert val == 'ReadyRole'
        assert mock_get_instance.call_count == 1

        instance.state = {}
        mock_get_instance.reset_mock()
        msg = 'Instance with id: %s, cannot be found.' \
              % provider.running_instance_id

        # Test exception raised if instance state not found
        with pytest.raises(EC2CloudException) as error:
            provider._get_instance_state()

        assert str(error.value) == msg
        assert mock_get_instance.call_count == 1

    @patch.object(EC2Cloud, '_get_instance_state')
    def test_ec2_is_instance_running(self, mock_get_instance_state):
        """Test ec2 provider is instance runnning method."""
        mock_get_instance_state.return_value = 'running'

        provider = EC2Cloud(**self.kwargs)
        assert provider._is_instance_running()
        assert mock_get_instance_state.call_count == 1

        mock_get_instance_state.return_value = 'stopped'
        mock_get_instance_state.reset_mock()

        provider = EC2Cloud(**self.kwargs)
        assert not provider._is_instance_running()
        assert mock_get_instance_state.call_count == 1

    @patch.object(EC2Cloud, '_wait_on_instance')
    @patch.object(EC2Cloud, '_connect')
    def test_ec2_launch_instance(self, mock_connect, mock_wait_on_instance):
        """Test ec2 provider launch instance method."""
        instance = MagicMock()
        instance.instance_id = 'i-123456789'
        instances = [instance]

        resource = MagicMock()
        resource.create_instances.return_value = instances

        mock_connect.return_value = resource

        provider = EC2Cloud(**self.kwargs)
        provider.subnet_id = 'subnet-123456789'
        provider.security_group_id = 'sg-123456789'
        provider._launch_instance()

        mock_wait_on_instance.assert_called_once_with('running', 600)
        assert instance.instance_id == provider.running_instance_id
        assert resource.create_instances.call_count == 1

    @patch.object(EC2Cloud, '_get_instance')
    def test_ec2_set_image_id(self, mock_get_instance):
        """Test ec2 provider set image id method."""
        instance = MagicMock()
        instance.image_id = 'ami-123456'
        mock_get_instance.return_value = instance

        provider = EC2Cloud(**self.kwargs)
        provider._set_image_id()

        assert provider.image_id == instance.image_id
        assert mock_get_instance.call_count == 1

    @patch.object(EC2Cloud, '_get_instance')
    def test_ec2_set_instance_ip(self, mock_get_instance):
        """Test ec2 provider set image id method."""
        instance = MagicMock()
        instance.public_ip_address = None
        instance.private_ip_address = None
        instance.network_interfaces = []
        mock_get_instance.return_value = instance

        provider = EC2Cloud(**self.kwargs)
        msg = 'IP address for instance cannot be found.'

        with pytest.raises(EC2CloudException) as error:
            provider._set_instance_ip()

        assert str(error.value) == msg
        assert mock_get_instance.call_count == 1
        mock_get_instance.reset_mock()

        instance.private_ip_address = '127.0.0.1'

        provider._set_instance_ip()
        assert provider.instance_ip == '127.0.0.1'
        assert mock_get_instance.call_count == 1
        mock_get_instance.reset_mock()

        network_interface = MagicMock()
        network_interface.ipv6_addresses = ['127.0.0.2']
        instance.network_interfaces = [network_interface]

        provider._set_instance_ip()
        assert provider.instance_ip == '127.0.0.2'
        assert mock_get_instance.call_count == 1
        mock_get_instance.reset_mock()

        instance.public_ip_address = '127.0.0.3'

        provider._set_instance_ip()
        assert provider.instance_ip == '127.0.0.3'
        assert mock_get_instance.call_count == 1

    @patch.object(EC2Cloud, '_wait_on_instance')
    @patch.object(EC2Cloud, '_get_instance')
    def test_ec2_start_instance(
        self, mock_get_instance, mock_wait_on_instance
    ):
        """Test ec2 start instance method."""
        instance = MagicMock()
        instance.start.return_value = None
        instance.wait_until_running.return_value = None
        mock_get_instance.return_value = instance

        provider = EC2Cloud(**self.kwargs)
        provider._start_instance()

        mock_wait_on_instance.assert_called_once_with('running', 600)
        assert mock_get_instance.call_count == 1

    @patch.object(EC2Cloud, '_wait_on_instance')
    @patch.object(EC2Cloud, '_get_instance')
    def test_ec2_stop_instance(
        self, mock_get_instance, mock_wait_on_instance
    ):
        """Test ec2 stop instance method."""
        instance = MagicMock()
        instance.stop.return_value = None
        instance.wait_until_stopped.return_value = None
        mock_get_instance.return_value = instance

        provider = EC2Cloud(**self.kwargs)
        provider._stop_instance()

        mock_wait_on_instance.assert_called_once_with('stopped', 600)
        assert mock_get_instance.call_count == 1

    @patch.object(EC2Cloud, '_get_instance')
    def test_ec2_terminate_instance(self, mock_get_instance):
        """Test ec2 terminate instance method."""
        instance = MagicMock()
        instance.terminate.return_value = None
        mock_get_instance.return_value = instance

        provider = EC2Cloud(**self.kwargs)
        provider._terminate_instance()
        assert mock_get_instance.call_count == 1

    @patch('time.sleep')
    @patch.object(EC2Cloud, '_get_instance')
    def test_ec2_get_console_log(self, mock_get_instance, mock_time):
        """Test ec2 get console log method."""
        instance = MagicMock()
        instance.console_output.return_value = {
            'Output': 'Console log output...'
        }
        mock_get_instance.return_value = instance

        provider = EC2Cloud(**self.kwargs)
        output = provider.get_console_log()
        assert output == 'Console log output...'
        assert mock_get_instance.call_count == 1
