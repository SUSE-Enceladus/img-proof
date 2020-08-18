# -*- coding: utf-8 -*-

"""Module for testing instances using SSH only."""

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

from img_proof.ipa_exceptions import SSHCloudException
from img_proof.ipa_cloud import IpaCloud


class SSHCloud(IpaCloud):
    """Class for testing instances in Azure."""
    cloud = 'ssh'

    def post_init(self):
        """Initialize SSH cloud class."""

        # Cannot cleanup SSH instance
        self.cleanup = False
        self.instance_ip = self.custom_args.get('ip_address')

        if not self.instance_ip:
            raise SSHCloudException(
                'IP address is required to connect to instance.'
            )

        if not self.ssh_private_key_file:
            raise SSHCloudException(
                'SSH private key file is required to connect to instance.'
            )

        if not self.ssh_user:
            raise SSHCloudException(
                'SSH user is required to connect to instance.'
            )

    def _is_instance_running(self):
        """
        Return True.

        Instance must be running with SSh cloud.
        """
        return True

    def _get_instance_state(self):
        """
        Do nothing.
        """
        pass

    def _get_instance(self):
        """
        Do nothing.
        """
        pass

    def get_console_log(self):
        """
        Return console log output if it is available.
        """
        return ''  # No console log for SSH backend

    def _launch_instance(self):
        """
        Do nothing.

        SSH instance must be running.
        """
        raise SSHCloudException(
            'SSH class cannot launch instances.'
        )

    def _set_image_id(self):
        """
        Do nothing.
        """
        raise SSHCloudException(
            'SSH class has no access to cloud API.'
        )

    def _set_instance_ip(self):
        """
        Do nothing.
        """
        raise SSHCloudException(
            'SSH class has no access to cloud API.'
        )

    def _start_instance(self):
        """
        Do nothing.
        """
        raise SSHCloudException(
            'SSH class has no access to cloud API.'
        )

    def _stop_instance(self):
        """
        Do nothing.
        """
        raise SSHCloudException(
            'SSH class has no access to cloud API.'
        )

    def _terminate_instance(self):
        """
        Do nothing.
        """
        raise SSHCloudException(
            'SSH class has no access to cloud API.'
        )
