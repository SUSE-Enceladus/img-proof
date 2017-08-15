#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""Ipa distro unit tests."""

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

from ipa.ipa_distro import Distro

from unittest.mock import MagicMock

import pytest


def test_distro_not_implemented_methods():
    """Confirm methods raise not implemented exception."""
    distro = Distro()
    methods = [
        'get_refresh_repo_cmd',
        'get_stop_ssh_service_cmd',
        'get_update_cmd'
    ]
    for method in methods:
        pytest.raises(
            NotImplementedError,
            getattr(distro, method)
        )

    client = MagicMock()
    pytest.raises(
        NotImplementedError,
        getattr(distro, '_set_init_system'),
        client
    )


def test_distro_get_commands():
    """Test distro reboot and sudo command return values."""
    distro = Distro()
    assert distro.get_reboot_cmd() == 'shutdown -r now'
    assert distro.get_sudo_exec_wrapper() == 'sudo sh -c'
