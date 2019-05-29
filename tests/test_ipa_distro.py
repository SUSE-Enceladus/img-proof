#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""img_proof distro unit tests."""

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

from img_proof.ipa_distro import Distro
from img_proof.ipa_exceptions import IpaDistroException

from unittest.mock import call, MagicMock, patch

import pytest

methods = [
    'get_install_cmd',
    'get_refresh_repo_cmd',
    'get_stop_ssh_service_cmd',
    'get_update_cmd'
]


@pytest.mark.parametrize(
    "method",
    methods,
    ids=methods
)
def test_distro_not_implemented_methods(method):
    """Confirm methods raise not implemented exception."""
    distro = Distro()
    pytest.raises(
        NotImplementedError,
        getattr(distro, method)
    )


def test_distro_set_init_system_exception():
    """Test distro set init system method exception."""
    client = MagicMock()
    distro = Distro()

    with patch('img_proof.ipa_utils.execute_ssh_command', MagicMock(
               side_effect=Exception('ERROR!'))) as mocked:
        pytest.raises(
            IpaDistroException,
            distro._set_init_system,
            client
        )

    mocked.assert_called_once_with(client, 'ps -p 1 -o comm=')


def test_distro_get_commands():
    """Test distro reboot and sudo command return values."""
    distro = Distro()
    assert distro.get_reboot_cmd() == 'shutdown -r now'
    assert distro.get_sudo_exec_wrapper() == 'sudo sh -c'


def test_distro_get_vm_info():
    """Test distro get vm info method."""
    client = MagicMock()
    distro = Distro()
    distro.init_system = 'systemd'

    with patch('img_proof.ipa_utils.execute_ssh_command',
               MagicMock(return_value='')) as mocked:
        distro.get_vm_info(client)

    mocked.assert_has_calls([
        call(client, 'systemd-analyze'),
        call(client, 'systemd-analyze blame'),
        call(client, 'sudo journalctl -b')
    ])
