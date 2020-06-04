#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""img_proof Fedora distro unit tests."""

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

from img_proof.ipa_fedora import Fedora

from unittest.mock import MagicMock, patch


def test_fedora_set_init_system():
    """Test Fedora set init system method."""
    client = MagicMock()
    fedora = Fedora()

    with patch('img_proof.ipa_utils.execute_ssh_command',
               MagicMock(return_value='systemd')) as mocked:
        fedora._set_init_system(client)

    assert fedora.init_system == 'systemd'
    mocked.assert_called_once_with(client, 'ps -p 1 -o comm=')
