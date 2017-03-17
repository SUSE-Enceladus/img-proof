# -*- coding: utf-8 -*-
#
# Copyright (c) 2017 SUSE LLC
#
# This file is part of ipa.
#
# See LICENSE for license information.

from ipa_distro import Distro


class SUSE(Distro):
    def __init__(self):
        super(SUSE, self).__init__()

    def get_stop_ssh_service_cmd(self):
        """Return command to stop SSH service for SUSE."""
        return 'sudo systemctl stop sshd'
