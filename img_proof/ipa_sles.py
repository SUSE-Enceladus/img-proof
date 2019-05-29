# -*- coding: utf-8 -*-

"""SLES distro module and sync points."""

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
from img_proof.ipa_exceptions import IpaSLESException


class SLES(Distro):
    """SLES distro class."""

    def get_install_cmd(self):
        """Return install package command for SLES."""
        return 'zypper -n --no-gpg-checks in -y'

    def get_refresh_repo_cmd(self):
        """Return refresh repo command for SLES."""
        return 'zypper -n refresh'

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
        return 'zypper -n up --auto-agree-with-licenses ' \
               '--force-resolution --replacefiles'
