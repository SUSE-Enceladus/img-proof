#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""img_proof Aliyun provider unit tests."""

# Copyright (c) 2020 SUSE LLC. All rights reserved.
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

from img_proof.ipa_aliyun import AliyunCloud
from img_proof.ipa_exceptions import AliyunCloudException

from unittest.mock import MagicMock, patch


class TestAliyunProvider(object):
    """Test Aliyun provider class."""

    def setup_method(self, method):
        """Set up kwargs dict."""
        self.kwargs = {
            'config': 'tests/data/config',
            'distro_name': 'SLES',
            'image_id': 'fakeimage',
            'no_default_test_dirs': True,
            'test_files': ['test_image'],
            'custom_args': {
                'access_key': '123',
                'access_secret': '321',
                'ssh_key_name': 'test-key'
            }
        }

    def test_exception_required_args(self):
        """Test an exception is raised if required args missing."""
        self.kwargs['config'] = 'tests/data/config.noregion'

        msg = 'Region is required to connect to Aliyun.'

        # Test region required
        with pytest.raises(AliyunCloudException) as error:
            AliyunCloud(**self.kwargs)

        assert str(error.value) == msg

        self.kwargs['config'] = 'tests/data/config'

    @patch('img_proof.ipa_aliyun.AcsClient')
    def test_bad_connection(self, mock_client):
        """Test an exception is raised if boto3 unable to connect."""
        mock_client.side_effect = Exception('ERROR!')

        provider = AliyunCloud(**self.kwargs)
        msg = 'Could not connect to region: %s' % provider.region

        # Test ssh private key file required
        with pytest.raises(AliyunCloudException) as error:
            provider._connect()

        assert str(error.value) == msg
        assert mock_client.call_count > 0

    @patch.object(AliyunCloud, '_connect')
    def test_get_instance(self, mock_connect):
        """Test get instance method."""
        response = '{"Instances": {"Instance": [{"name": "test instance"}]}}'
        client = MagicMock()
        client.do_action_with_exception.return_value = response
        mock_connect.return_value = client

        provider = AliyunCloud(**self.kwargs)
        val = provider._get_instance()
        assert val['name'] == 'test instance'

    @patch.object(AliyunCloud, '_connect')
    def test_get_instance_error(self, mock_connect):
        """Test get instance method error."""
        client = MagicMock()
        client.do_action_with_exception.side_effect = Exception('Error!')
        mock_connect.return_value = client

        provider = AliyunCloud(**self.kwargs)
        provider.running_instance_id = 'i-123456789'

        with pytest.raises(AliyunCloudException) as error:
            provider._get_instance()

        msg = 'Instance with ID: i-123456789 not found.'
        assert str(error.value) == msg

    @patch.object(AliyunCloud, '_get_instance')
    def test_get_instance_state(self, mock_get_instance):
        """Test an exception is raised if client unable to connect."""
        instance = {'Status': 'Running'}
        mock_get_instance.return_value = instance

        provider = AliyunCloud(**self.kwargs)
        provider.running_instance_id = 'i-123456789'

        val = provider._get_instance_state()
        assert val == 'Running'

        del instance['Status']
        msg = 'Status of instance with id: %s, cannot be found.' \
              % provider.running_instance_id

        # Test exception raised if instance state not found
        with pytest.raises(AliyunCloudException) as error:
            provider._get_instance_state()

        assert str(error.value) == msg

    @patch.object(AliyunCloud, '_get_instance_state')
    def test_is_instance_running(self, mock_get_instance_state):
        """Test aliyun provider is instance runnning method."""
        mock_get_instance_state.return_value = 'Running'

        provider = AliyunCloud(**self.kwargs)
        assert provider._is_instance_running()

        mock_get_instance_state.return_value = 'Stopped'

        provider = AliyunCloud(**self.kwargs)
        assert not provider._is_instance_running()

    @patch.object(AliyunCloud, '_wait_on_instance')
    @patch.object(AliyunCloud, '_connect')
    def test_launch_instance(self, mock_connect, mock_wait_on_instance):
        """Test aliyun provider launch instance method."""
        response = json.dumps({
            'InstanceIdSets': {
                'InstanceIdSet': ['i-123456789']
            }
        })

        client = MagicMock()
        client.do_action_with_exception.return_value = response
        mock_connect.return_value = client

        provider = AliyunCloud(**self.kwargs)
        provider.v_switch_id = 'v-123456789'
        provider.security_group_id = 'sg-123456789'
        provider._launch_instance()

        mock_wait_on_instance.assert_called_once_with('Running', 600)
        assert 'i-123456789' == provider.running_instance_id

    @patch.object(AliyunCloud, '_get_instance')
    def test_set_image_id(self, mock_get_instance):
        """Test aliyun provider set image id method."""
        instance = {'ImageId': 'ami-123456'}
        mock_get_instance.return_value = instance

        provider = AliyunCloud(**self.kwargs)
        provider._set_image_id()

        assert provider.image_id == 'ami-123456'

    @patch.object(AliyunCloud, '_get_instance')
    def test_set_instance_ip(self, mock_get_instance):
        """Test aliyun provider set image id method."""
        instance = {
            'PublicIpAddress': {'IpAddress': ['8.13.21.34']},
            'InnerIpAddress': {'IpAddress': ['10.10.01.01']}
        }
        mock_get_instance.return_value = instance

        provider = AliyunCloud(**self.kwargs)
        provider._set_instance_ip()

        assert provider.instance_ip == '8.13.21.34'

        msg = 'IP address for instance cannot be found.'
        instance = {
            'PublicIpAddress': {'IpAddress': []},
            'InnerIpAddress': {'IpAddress': []}
        }
        mock_get_instance.return_value = instance

        with pytest.raises(AliyunCloudException) as error:
            provider._set_instance_ip()

        assert str(error.value) == msg

    @patch.object(AliyunCloud, '_wait_on_instance')
    @patch.object(AliyunCloud, '_connect')
    def test_start_instance(
        self, mock_connect, mock_wait_on_instance
    ):
        """Test aliyun start instance method."""
        client = MagicMock()
        mock_connect.return_value = client

        provider = AliyunCloud(**self.kwargs)
        provider._start_instance()

        mock_wait_on_instance.assert_called_once_with('Running', 600)
        assert client.do_action_with_exception.call_count == 1

    @patch.object(AliyunCloud, '_wait_on_instance')
    @patch.object(AliyunCloud, '_connect')
    def test_stop_instance(
        self, mock_connect, mock_wait_on_instance
    ):
        """Test aliyun stop instance method."""
        client = MagicMock()
        mock_connect.return_value = client

        provider = AliyunCloud(**self.kwargs)
        provider._stop_instance()

        mock_wait_on_instance.assert_called_once_with('Stopped', 600)
        assert client.do_action_with_exception.call_count == 1

    @patch.object(AliyunCloud, '_connect')
    def test_terminate_instance(self, mock_connect):
        """Test aliyun terminate instance method."""
        client = MagicMock()
        mock_connect.return_value = client

        provider = AliyunCloud(**self.kwargs)
        provider._terminate_instance()
        assert client.do_action_with_exception.call_count == 1

    @patch.object(AliyunCloud, '_connect')
    def test_get_console_log(self, mock_connect):
        """Test aliyun get console log method."""
        response = json.dumps({
            'ConsoleOutput': 'TXVsdGkgbGluZQoKQ29uc29sZSBsb2cgb3V0cHV0Li4u'
        })

        client = MagicMock()
        client.do_action_with_exception.return_value = response
        mock_connect.return_value = client

        provider = AliyunCloud(**self.kwargs)
        output = provider.get_console_log()
        assert output == 'Multi line\n\nConsole log output...'
