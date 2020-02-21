# -*- coding: utf-8 -*-

"""Distro module provides distribution specific synch points."""

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

from img_proof import ipa_utils
from img_proof.ipa_constants import NOT_IMPLEMENTED
from img_proof.ipa_exceptions import IpaDistroException


class Distro(object):
    """Generic module for performing instance level tests."""

    def __init__(self):
        """Initialize distro class."""
        super(Distro, self).__init__()
        self.init_system = ''

    def _set_init_system(self, client):
        """Determine the init system of distribution."""
        if not self.init_system:
            try:
                out = ipa_utils.execute_ssh_command(
                    client,
                    'ps -p 1 -o comm='
                )
            except Exception as e:
                raise IpaDistroException(
                    'An error occurred while retrieving'
                    ' the distro init system: %s' % e
                )
            if out:
                self.init_system = out.strip()

    def get_install_cmd(self):
        """Return install package command for distribution."""
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

    def get_vm_info(self, client):
        """Return vm info."""
        out = ''
        self._set_init_system(client)

        if self.init_system == 'systemd':
            try:
                out += 'systemd-analyze:\n\n'
                out += ipa_utils.execute_ssh_command(
                    client,
                    'systemd-analyze'
                )

                out += 'systemd-analyze blame:\n\n'
                out += ipa_utils.execute_ssh_command(
                    client,
                    'systemd-analyze blame'
                )

                out += 'journalctl -b:\n\n'
                out += ipa_utils.execute_ssh_command(
                    client,
                    'sudo journalctl -b'
                )
            except Exception as error:
                out = 'Failed to collect VM info: {0}.'.format(error)

        return out

    def install_package(self, client, package):
        """Install package on instance."""
        install_cmd = "{sudo} '{install} {package}'".format(
            sudo=self.get_sudo_exec_wrapper(),
            install=self.get_install_cmd(),
            package=package
        )

        try:
            out = ipa_utils.execute_ssh_command(
                client,
                install_cmd
            )
        except Exception as error:
            raise IpaDistroException(
                'An error occurred installing package {package} '
                'on instance: {error}'.format(
                    package=package,
                    error=error
                )
            )
        else:
            return out

    def reboot(self, client):
        """Execute reboot command on instance."""
        self._set_init_system(client)

        reboot_cmd = \
            "{sudo} '(sleep 1 && {stop_ssh} && {reboot} &)' && exit".format(
                sudo=self.get_sudo_exec_wrapper(),
                stop_ssh=self.get_stop_ssh_service_cmd(),
                reboot=self.get_reboot_cmd()
            )

        try:
            transport = client.get_transport()
            channel = transport.open_session()
            channel.exec_command(reboot_cmd)
            time.sleep(2)  # Required for delay in reboot
            transport.close()
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

    def repo_refresh(self, client):
        """Execute repo refresh command on instance."""
        update_cmd = "{sudo} '{refresh}'".format(
            sudo=self.get_sudo_exec_wrapper(),
            refresh=self.get_refresh_repo_cmd()
        )

        out = ''
        try:
            out = ipa_utils.execute_ssh_command(
                client,
                update_cmd
            )
        except Exception as error:
            raise IpaDistroException(
                'An error occurred refreshing repos on instance: %s' % error
            )
        return out
