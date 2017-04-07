# -*- coding: utf-8 -*-
#
# Copyright (c) 2017 SUSE LLC
#
# This file is part of ipa.
#
# See LICENSE for license information.

import ipa_utils
from ipa_distro import Distro
from ipa_exceptions import IpaDistroException


class SUSE(Distro):
    def __init__(self, client):
        super(SUSE, self).__init__(client)

    def _set_init_system(self, client):
        """Determine the init system of distribution."""
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

    def get_stop_ssh_service_cmd(self):
        """Return command to stop SSH service for SUSE."""
        if self.init_system == 'systemd':
            return 'systemctl stop sshd'
        elif self.init_system == 'init':
            return 'rcsshd stop'
        else:
            raise IpaDistroException(
                'The init system for SUSE distribution cannot be determined.'
            )
