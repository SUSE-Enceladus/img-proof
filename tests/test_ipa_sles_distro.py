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


def test_sles_install_package():
    """Test install package method for SLES distro."""
    client = MagicMock()
    sles = SLES()

    with patch('ipa.ipa_utils.execute_ssh_command',
               MagicMock(return_value='')) as mocked:
        sles.install_package(client, 'python')

    mocked.assert_called_once_with(
        client,
        "sudo sh -c 'zypper -n --no-gpg-checks in -y python'"
    )


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


def test_sles_update_file_conflict():
    """Test update method when update has file conflicts."""
    client = MagicMock()
    sles = SLES()

    file_conf_msg = (
        'error\nDetected 3 file conflicts:\n\nFile '
        '/etc/issue\n  from install of\n     '
        'SLES_SAP-release-12.1-2.1.x86_64 (SLE-12-SP1-SAP-Updates)\r\n  '
        'conflicts with file from package\n     '
        'sles-release-12.1-1.331.x86_64 (@System)\n\nFile /etc/issue.net'
        '\n  from install of\n     SLES_SAP-release-12.1-2.1.x86_64 '
        '(SLE-12-SP1-SAP-Updates)\n  conflicts with file from package'
        '\n     sles-release-12.1-1.331.x86_64 (@System)\n\nFile /etc/'
        'os-release\n  from install of\n     '
        'SLES_SAP-release-12.1-2.1.x86_64 (SLE-12-SP1-SAP-Updates)\n  '
        'conflicts with file from package\n     '
        'sles-release-12.1-1.331.x86_64 (@System)\n\nFile conflicts '
        'happen when two packages attempt to install '
        'files with the same name but different contents. If you continue, '
        'conflicting files will be replaced losing the previous content.\n'
        'Continue? [yes/no] (no): \n\n'
        'Problem occured during or after installation or '
        'removal of packages:\nInstallation aborted by user\n\n'
        'Please see the above error message for a hint.\n'
    )
    with patch('ipa.ipa_utils.execute_ssh_command', MagicMock(
            return_value=file_conf_msg)) as mocked:
        output = sles.update(client)

    mocked.assert_called_once_with(
        client,
        "sudo sh -c 'zypper -n refresh;zypper -n up "
        "--auto-agree-with-licenses --force-resolution'"
    )
    assert output == ''
