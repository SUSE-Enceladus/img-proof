# -*- coding: utf-8 -*-

"""Distro module provides distrobution specific synch points."""

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

from ipa import ipa_utils
from ipa.ipa_constants import NOT_IMPLEMENTED
from ipa.ipa_exceptions import IpaDistroException


class Distro(object):
    """Generic module for performing instance level tests."""

    def __init__(self):
        """Initialize distro class."""
        super(Distro, self).__init__()
        self.init_system = ''

    def _set_init_system(self, client):
        """Determine the init system of distribution."""
        raise NotImplementedError(NOT_IMPLEMENTED)

    def get_reboot_cmd(self):
        """Return reboot command for given distribution."""
        return 'shutdown -r now'

    def get_refresh_repo_cmd(self):
        """Return refresh repo command for distribution."""
        raise NotImplementedError(NOT_IMPLEMENTED)

    def get_stop_ssh_service_cmd(self):
        """Return command to stop SSH service on given distribution."""
        raise NotImplementedError(NOT_IMPLEMENTED)

    def get_sudo_exec_wrapper(self):
        """Return sudo command to wrap one or more commands."""
        return 'sudo sh -c'

    def get_update_cmd(self):
        """Return command to update instance."""
        raise NotImplementedError(NOT_IMPLEMENTED)

    def reboot(self, client):
        """Execute reboot command on instance."""
        if not self.init_system:
            self._set_init_system(client)

        reboot_cmd = "{sudo} '{stop_ssh};{reboot}'".format(
            sudo=self.get_sudo_exec_wrapper(),
            stop_ssh=self.get_stop_ssh_service_cmd(),
            reboot=self.get_reboot_cmd()
        )

        try:
            ipa_utils.execute_ssh_command(
                client,
                reboot_cmd
            )
        except Exception as error:
            raise IpaDistroException(
                'An error occurred rebooting instance: %s' % error
            )
        ipa_utils.clear_cache()

    def update(self, client):
        """Execute update command on instance."""
        update_cmd = "{sudo} '{refresh};{update}'".format(
            sudo=self.get_sudo_exec_wrapper(),
            refresh=self.get_refresh_repo_cmd(),
            update=self.get_update_cmd()
        )

        out = ''
        try:
            out = ipa_utils.execute_ssh_command(
                client,
                update_cmd
            )
        except Exception as error:
            raise IpaDistroException(
                'An error occurred updating instance: %s' % error
            )
        return out
