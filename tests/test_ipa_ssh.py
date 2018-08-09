#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""Ipa SSH provider unit tests."""

# Copyright (c) 2018 SUSE LLC
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

from ipa.ipa_exceptions import SSHProviderException
from ipa.ipa_ssh import SSHProvider


class TestSSHProvider(object):
    """Test SSH provider class."""

    def setup_method(self, method):
        """Set up kwargs dict."""
        self.kwargs = {
            'config': 'tests/data/config',
            'distro_name': 'sles',
            'ip_address': '10.0.0.1',
            'no_default_test_dirs': True,
            'ssh_private_key_file': 'tests/data/ida_test',
            'ssh_user': 'root',
            'test_dirs': 'tests/data/tests',
            'test_files': ['test_image']
        }

    @pytest.mark.parametrize('name,msg', [
        ('ssh_user', 'SSH user is required to connect to instance.'),
        (
            'ssh_private_key_file',
            'SSH private key file is required to connect to instance.'
        ),
        ('ip_address', 'IP address is required to connect to instance.')
    ])
    def test_required_args(self, name, msg):
        self.kwargs[name] = None

        with pytest.raises(SSHProviderException) as error:
            SSHProvider(**self.kwargs)

        assert str(error.value) == msg

    @pytest.mark.parametrize('name,result', [
        ('_is_instance_running', True),
        ('_get_instance_state', None),
        ('_get_instance', None)
    ])
    def test_ssh_empty_methods(self, name, result):
        """Test empty methods."""
        provider = SSHProvider(**self.kwargs)
        output = getattr(provider, name)()

        assert output == result

    @pytest.mark.parametrize('name,msg', [
        ('_launch_instance', 'SSH provider cannot launch instances.'),
        ('_set_image_id', 'SSH provider has no access to cloud API.'),
        ('_set_instance_ip', 'SSH provider has no access to cloud API.'),
        ('_start_instance', 'SSH provider has no access to cloud API.'),
        ('_stop_instance', 'SSH provider has no access to cloud API.'),
        ('_terminate_instance', 'SSH provider has no access to cloud API.')
    ])
    def test_ssh_not_implemented_methods(self, name, msg):
        """Test an exception is raised for methods that are not implemeted."""
        provider = SSHProvider(**self.kwargs)

        # Assert exception is raised
        with pytest.raises(SSHProviderException) as error:
            getattr(provider, name)()

        assert str(error.value) == msg
