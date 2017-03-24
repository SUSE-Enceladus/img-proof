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
    def __init__(self, instance_ip, ssh_private_key, ssh_user):
        super(SUSE, self).__init__(instance_ip,
                                   ssh_private_key,
                                   ssh_user)

    def _set_init_system(self, instance_ip, ssh_private_key, ssh_user):
        """Determine the init system of distribution."""
        out, err = ipa_utils.execute_ssh_command(
            'ps -p 1 -o comm=',
            instance_ip,
            ssh_private_key,
            ssh_user
        )
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
