# -*- coding: utf-8 -*-

"""SLES distro module and sync points."""

# Copyright (c) 2017 SUSE LLC
#
# This file is part of ipa.
#
# See LICENSE for license information.

from ipa import ipa_utils
from ipa.ipa_distro import Distro
from ipa.ipa_exceptions import IpaSLESException


class SLES(Distro):
    """SLES distro class."""

    def _set_init_system(self, client):
        """Determine the init system of distribution."""
        try:
            out = ipa_utils.execute_ssh_command(
                client,
                'ps -p 1 -o comm='
            )
        except Exception as e:
            raise IpaSLESException(
                'An error occurred while retrieving'
                ' the distro init system: %s' % e
            )
        if out:
            self.init_system = out.strip()

    def get_refresh_repo_cmd(self):
        """Return refresh repo command for SLES."""
        return 'zypper refresh'

    def get_stop_ssh_service_cmd(self):
        """
        Return command to stop SSH service for SLES.

        SSH stop command determined by init system.
        """
        if self.init_system == 'systemd':
            return 'systemctl stop sshd.service'
        elif self.init_system == 'init':
            return 'rcsshd stop'
        else:
            raise IpaSLESException(
                'The init system for SUSE distribution cannot be determined.'
            )

    def get_update_cmd(self):
        """Return command to update SLES instance."""
        return 'zypper up --no-confirm'
