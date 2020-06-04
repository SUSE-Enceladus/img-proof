#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""img_proof Red Hat distro unit tests."""

# Copyright (c) 2020 Neal Gompa. All rights reserved.
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

import pytest

from img_proof.ipa_exceptions import IpaDistroException, IpaRedHatException
from img_proof.ipa_redhat import RedHat

from unittest.mock import MagicMock, patch


def test_redhat_get_stop_ssh_cmd():
    """Test Red Hat get stop ssh cmd method."""
    redhat = RedHat()

    redhat.init_system = 'systemd'
    assert redhat.get_stop_ssh_service_cmd() == 'systemctl stop sshd.service'

    redhat.init_system = 'init'
    assert redhat.get_stop_ssh_service_cmd() == 'service sshd stop'

    redhat.init_system = 'fake'
    with pytest.raises(IpaRedHatException) as error:
        redhat.get_stop_ssh_service_cmd()
    assert str(error.value) == \
        'The init system for this Red Hat system cannot be determined.'


def test_redhat_install_package():
    """Test install package method for Red Hat distro."""
    client = MagicMock()
    redhat = RedHat()

    with patch('img_proof.ipa_utils.execute_ssh_command',
               MagicMock(return_value='')) as mocked:
        redhat.install_package(client, 'python')

    mocked.assert_called_once_with(
        client,
        "sudo sh -c 'dnf --assumeyes --nogpgcheck install python'"
    )


@patch('img_proof.ipa_distro.time')
def test_redhat_reboot(mock_time):
    """Test soft reboot method for Red Hat distro."""
    client = MagicMock()
    channel = MagicMock()
    transport = MagicMock()
    transport.open_session.return_value = channel
    client.get_transport.return_value = transport
    redhat = RedHat()
    redhat.init_system = 'systemd'

    redhat.reboot(client)

    channel.exec_command.assert_called_once_with(
        "sudo sh -c '(sleep 1 && systemctl stop sshd.service "
        "&& shutdown -r now &)' && exit"
    )


def test_redhat_reboot_exception():
    """Test soft reboot method exception for Red Hat distro."""
    client = MagicMock()
    client.get_transport.side_effect = Exception('ERROR!')
    redhat = RedHat()
    redhat.init_system = 'systemd'

    with pytest.raises(IpaDistroException):
        redhat.reboot(client)


def test_redhat_update():
    """Test update method for Red Hat distro."""
    client = MagicMock()
    redhat = RedHat()

    with patch('img_proof.ipa_utils.execute_ssh_command',
               MagicMock(return_value='Update finished!')) as mocked:
        output = redhat.update(client)

    mocked.assert_called_once_with(
        client,
        "sudo sh -c 'dnf --assumeyes makecache;dnf --assumeyes upgrade'"
    )
    assert output == 'Update finished!'


def test_redhat_update_exception():
    """Test update method exception for Red Hat distro."""
    client = MagicMock()
    redhat = RedHat()

    with patch('img_proof.ipa_utils.execute_ssh_command', MagicMock(
               side_effect=Exception('ERROR!'))) as mocked:
        pytest.raises(
            IpaDistroException,
            redhat.update,
            client
        )

    mocked.assert_called_once_with(
        client,
        "sudo sh -c 'dnf --assumeyes makecache;dnf --assumeyes upgrade'"
    )


def test_redhat_refresh():
    """Test refresh method for Red Hat distro."""
    client = MagicMock()
    redhat = RedHat()

    with patch('img_proof.ipa_utils.execute_ssh_command',
               MagicMock(return_value='Refresh finished!')) as mocked:
        output = redhat.repo_refresh(client)

    mocked.assert_called_once_with(
        client,
        "sudo sh -c 'dnf --assumeyes makecache'"
    )
    assert output == 'Refresh finished!'


def test_redhat_refresh_exception():
    """Test refresh method exception for Red Hat distro."""
    client = MagicMock()
    redhat = RedHat()

    with patch('img_proof.ipa_utils.execute_ssh_command', MagicMock(
            side_effect=Exception('ERROR!'))) as mocked:
        pytest.raises(
            IpaDistroException,
            redhat.repo_refresh,
            client
        )

    mocked.assert_called_once_with(
        client,
        "sudo sh -c 'dnf --assumeyes makecache'"
    )
