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

import time

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


@patch('img_proof.ipa_distro.time')
def test_distro_set_init_system_exception(mock_time):
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

    mocked.assert_has_calls([
        call(client, 'ps -p 1 -o comm='),
        call(client, 'ps -p 1 -o comm='),
        call(client, 'ps -p 1 -o comm=')
    ])


def test_distro_get_commands():
    """Test distro reboot and sudo command return values."""
    distro = Distro()
    assert distro.get_reboot_cmd() == 'shutdown -r now'
    assert distro.get_sudo_exec_wrapper() == 'sudo sh -c'


@patch('img_proof.ipa_distro.ipa_utils.clear_cache')
@patch('img_proof.ipa_distro.time.sleep')
def test_distro_reboot(mock_sleep, mock_clear_cache):
    """Test distro reboot happy path execs the reboot command."""
    client = MagicMock()
    transport = client.get_transport.return_value
    channel = transport.open_session.return_value
    distro = Distro()
    distro.init_system = 'systemd'
    distro.get_stop_ssh_service_cmd = MagicMock(
        return_value='systemctl stop sshd'
    )

    distro.reboot(client)

    from img_proof.ipa_distro import REBOOT_EXEC_TIMEOUT
    transport.open_session.assert_called_once_with(timeout=REBOOT_EXEC_TIMEOUT)

    expected_cmd = (
        "sudo sh -c '(sleep 1 && systemctl stop sshd &&"
        " shutdown -r now &)' && exit"
    )
    channel.exec_command.assert_called_once_with(expected_cmd)

    mock_sleep.assert_called_once_with(2)
    transport.close.assert_called_once()
    mock_clear_cache.assert_called_once()


@patch('img_proof.ipa_distro.ipa_utils.clear_cache')
@patch('img_proof.ipa_distro.time.sleep')
def test_distro_reboot_exec_timeout(mock_sleep, mock_clear_cache):
    """Test distro reboot closes transport instead of hanging when exec_command
    never returns."""
    client = MagicMock()
    transport = client.get_transport.return_value
    channel = transport.open_session.return_value
    import threading
    channel.exec_command.side_effect = lambda cmd: threading.Event().wait(0.1)
    distro = Distro()
    distro.init_system = 'systemd'
    distro.get_stop_ssh_service_cmd = MagicMock(
        return_value='systemctl stop sshd'
    )

    with patch('img_proof.ipa_distro.REBOOT_EXEC_TIMEOUT', 0.05):
        distro.reboot(client)

    transport.open_session.assert_called_once_with(timeout=0.05)
    mock_sleep.assert_not_called()
    transport.close.assert_called_once()
    mock_clear_cache.assert_called_once()


@patch('img_proof.ipa_distro.ipa_utils.clear_cache')
def test_distro_reboot_exec_error(mock_clear_cache):
    """Test distro reboot wraps exec_command errors."""
    client = MagicMock()
    transport = client.get_transport.return_value
    channel = transport.open_session.return_value
    channel.exec_command.side_effect = Exception('Broken pipe')
    distro = Distro()
    distro.init_system = 'systemd'
    distro.get_stop_ssh_service_cmd = MagicMock(
        return_value='systemctl stop sshd'
    )

    with pytest.raises(IpaDistroException) as excinfo:
        distro.reboot(client)

    assert 'An error occurred rebooting instance: Broken pipe' \
        in str(excinfo.value)
    mock_clear_cache.assert_called_once()
    transport.close.assert_not_called()


def test_distro_get_vm_info():
    """Test distro get vm info method."""
    client = MagicMock()
    distro = Distro()
    distro.init_system = 'systemd'

    with patch(
        'img_proof.ipa_utils.execute_ssh_command',
        MagicMock(return_value='')
    ) as mocked:
        distro.get_vm_info(client)

    mocked.assert_has_calls([
        call(client, 'systemd-analyze'),
        call(client, 'systemd-analyze blame'),
        call(client, 'sudo journalctl -b')
    ])
