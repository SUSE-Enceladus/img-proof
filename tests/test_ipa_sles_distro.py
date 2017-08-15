#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""Ipa SLES distro unit tests."""

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

from ipa.ipa_exceptions import IpaDistroException, IpaSLESException
from ipa.ipa_sles import SLES

from unittest.mock import MagicMock, patch


def test_sles_set_init_system_exception():
    """Test SLES set init system method exception."""
    client = MagicMock()
    sles = SLES()

    with patch('ipa.ipa_utils.execute_ssh_command', MagicMock(
               side_effect=Exception('ERROR!'))) as mocked:
        pytest.raises(
            IpaSLESException,
            sles._set_init_system,
            client
        )

    mocked.assert_called_once_with(client, 'ps -p 1 -o comm=')


def test_sles_get_stop_ssh_cmd():
    """Test SLES get stop ssh cmd method."""
    sles = SLES()

    sles.init_system = 'systemd'
    assert sles.get_stop_ssh_service_cmd() == 'systemctl stop sshd.service'

    sles.init_system = 'init'
    assert sles.get_stop_ssh_service_cmd() == 'rcsshd stop'

    sles.init_system = 'fake'
    with pytest.raises(IpaSLESException) as error:
        sles.get_stop_ssh_service_cmd()
    assert str(error.value) == \
        'The init system for SUSE distribution cannot be determined.'


def test_sles_reboot():
    """Test soft reboot method for SLES distro."""
    client = MagicMock()
    sles = SLES()
    sles.init_system = 'systemd'

    with patch('ipa.ipa_utils.execute_ssh_command',
               MagicMock(return_value='')) as mocked:
        sles.reboot(client)

    mocked.assert_called_once_with(
        client,
        "sudo sh -c 'systemctl stop sshd.service;shutdown -r now'"
    )


def test_sles_reboot_exception():
    """Test soft reboot method exception for SLES distro."""
    client = MagicMock()
    sles = SLES()
    sles.init_system = 'systemd'

    with patch('ipa.ipa_utils.execute_ssh_command', MagicMock(
               side_effect=Exception('ERROR!'))) as mocked:
        pytest.raises(
            IpaDistroException,
            sles.reboot,
            client
        )

    mocked.assert_called_once_with(
        client,
        "sudo sh -c 'systemctl stop sshd.service;shutdown -r now'"
    )


def test_sles_update():
    """Test update method for SLES distro."""
    client = MagicMock()
    sles = SLES()

    with patch('ipa.ipa_utils.execute_ssh_command',
               MagicMock(return_value='Update finished!')) as mocked:
        output = sles.update(client)

    mocked.assert_called_once_with(
        client,
        "sudo sh -c 'zypper -n refresh;zypper -n up "
        "--auto-agree-with-licenses --force-resolution'"
    )
    assert output == 'Update finished!'


def test_sles_update_exception():
    """Test update method exception for SLES distro."""
    client = MagicMock()
    sles = SLES()

    with patch('ipa.ipa_utils.execute_ssh_command', MagicMock(
               side_effect=Exception('ERROR!'))) as mocked:
        pytest.raises(
            IpaDistroException,
            sles.update,
            client
        )

    mocked.assert_called_once_with(
        client,
        "sudo sh -c 'zypper -n refresh;zypper -n up "
        "--auto-agree-with-licenses --force-resolution'"
    )
