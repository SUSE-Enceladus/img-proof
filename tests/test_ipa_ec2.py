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

    @patch('libcloud.compute.drivers.ec2.EC2NodeDriver')
    def test_gce_get_driver(self, mock_node_driver):
        """Test ec2 get driver method."""
        driver = MagicMock()
        mock_node_driver.return_value = driver

        provider = EC2Provider(**self.kwargs)
        assert driver == provider.compute_driver

    @patch.object(EC2Provider, '_get_driver')
    def test_ec2_get_instance(self, mock_get_driver):
        """Test get instance method."""
        instance = MagicMock()
        driver = MagicMock()
        mock_get_driver.return_value = driver
        driver.list_nodes.return_value = [instance]

        provider = EC2Provider(**self.kwargs)
        val = provider._get_instance()
        assert val == instance
        assert driver.list_nodes.call_count == 1

    @patch.object(EC2Provider, '_get_driver')
    def test_ec2_get_instance_not_found(self, mock_get_driver):
        """Test get instance method."""
        driver = MagicMock()
        mock_get_driver.return_value = driver
        driver.list_nodes.return_value = []

        self.kwargs['running_instance_id'] = 'i-123456789'
        provider = EC2Provider(**self.kwargs)

        with pytest.raises(EC2ProviderException) as error:
            provider._get_instance()

        assert str(error.value) == 'Instance with ID: i-123456789 not found.'
        assert driver.list_nodes.call_count == 1

    @patch.object(EC2Provider, '_get_driver')
    def test_ec2_launch_instance(self, mock_get_driver):
        """Test ec2 provider launch instance method."""
        driver = MagicMock()

        size = MagicMock()
        size.id = 't2.micro'
        driver.list_sizes.return_value = [size]

        image = MagicMock()
        image.id = 'fakeimage'
        driver.list_images.return_value = [image]

        instance = MagicMock()
        instance.id = 'i-123456789'
        driver.create_node.return_value = instance

        mock_get_driver.return_value = driver

        provider = EC2Provider(**self.kwargs)
        provider._launch_instance()

        assert instance.id == provider.running_instance_id
        assert driver.list_sizes.call_count == 1
        assert driver.list_images.call_count == 1
        assert driver.create_node.call_count == 1

    @patch.object(EC2Provider, '_get_driver')
    def test_ec2_launch_no_key_name(self, mock_get_driver):
        """Test ec2 provider raises exception if no ssh key name method."""
        driver = MagicMock()
        mock_get_driver.return_value = driver

        provider = EC2Provider(**self.kwargs)
        provider.ssh_key_name = None
        msg = 'SSH Key Name is required to launch an EC2 instance.'

        with pytest.raises(EC2ProviderException) as error:
            provider._launch_instance()

        assert str(error.value) == msg

    @patch.object(EC2Provider, '_get_driver')
    def test_ec2_launch_instance_no_size(self, mock_get_driver):
        """Test exception raised if instance type not found."""
        driver = MagicMock()
        driver.list_sizes.return_value = []

        mock_get_driver.return_value = driver
        provider = EC2Provider(**self.kwargs)

        with pytest.raises(EC2ProviderException) as error:
            provider._launch_instance()

        assert str(error.value) == 'Instance type: t2.micro not found.'
        assert driver.list_sizes.call_count == 1

    @patch.object(EC2Provider, '_get_driver')
    def test_ec2_launch_instance_no_image(self, mock_get_driver):
        """Test exception raised if image not found."""
        driver = MagicMock()

        size = MagicMock()
        size.id = 't2.micro'
        driver.list_sizes.return_value = [size]
        driver.list_images.return_value = []

        mock_get_driver.return_value = driver
        provider = EC2Provider(**self.kwargs)

        with pytest.raises(EC2ProviderException) as error:
            provider._launch_instance()

        assert str(error.value) == 'Image with ID: fakeimage not found.'
        assert driver.list_sizes.call_count == 1
        assert driver.list_images.call_count == 1

    @patch.object(EC2Provider, '_get_instance')
    @patch.object(EC2Provider, '_get_driver')
    def test_ec2_set_image_id(self, mock_get_driver, mock_get_instance):
        """Test ec2 provider set image id method."""
        instance = MagicMock()
        instance.extra = {'image_id': 'ami-123456'}
        mock_get_instance.return_value = instance
        mock_get_driver.return_value = None

        provider = EC2Provider(**self.kwargs)
        provider._set_image_id()

        assert provider.image_id == instance.extra['image_id']
        assert mock_get_instance.call_count == 1
