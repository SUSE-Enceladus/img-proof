# -*- coding: utf-8 -*-

"""Module for testing instances using SSH only."""

# Copyright (c) 2018 SUSE LLC
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

import os

from ipa.ipa_exceptions import SSHProviderException
from ipa.ipa_provider import IpaProvider


class SSHProvider(IpaProvider):
    """Class for testing instances in Azure."""

    def __init__(self,
                 accelerated_networking=None,  # Not used in SSH
                 access_key_id=None,  # Not used in SSH
                 account_name=None,  # Not used in SSH
                 cleanup=None,
                 config=None,
                 description=None,
                 distro_name=None,
                 early_exit=None,
                 history_log=None,
                 image_id=None,  # Not used in SSH
                 inject=None,
                 instance_type=None,  # Not used in SSH
                 ip_address=None,
                 log_level=30,
                 no_default_test_dirs=False,
                 provider_config=None,
                 region=None,  # Not used in SSH
                 results_dir=None,
                 running_instance_id=None,  # Not used in SSH
                 secret_access_key=None,  # Not used in SSH
                 security_group_id=None,  # Not used in SSH
                 service_account_file=None,  # Not used in SSH
                 ssh_key_name=None,  # Not used in SSH
                 ssh_private_key_file=None,
                 ssh_user=None,
                 subnet_id=None,  # Not used in SSH
                 test_dirs=None,
                 test_files=None,
                 timeout=None,
                 vnet_name=None,  # Not used in SSH
                 vnet_resource_group=None,  # Not used in SSH
                 collect_vm_info=None):
        """Initialize Azure Provider class."""
        super(SSHProvider, self).__init__('ssh',
                                          cleanup,
                                          config,
                                          description,
                                          distro_name,
                                          early_exit,
                                          history_log,
                                          image_id,
                                          inject,
                                          instance_type,
                                          log_level,
                                          no_default_test_dirs,
                                          provider_config,
                                          region,
                                          results_dir,
                                          running_instance_id,
                                          test_dirs,
                                          test_files,
                                          timeout,
                                          collect_vm_info)

        # Cannot cleanup SSH instance
        self.cleanup = False

        self.ssh_private_key_file = (
            ssh_private_key_file or
            self._get_value(
                ssh_private_key_file, 'ssh_private_key_file'
            )
        )
        if not self.ssh_private_key_file:
            raise SSHProviderException(
                'SSH private key file is required to connect to instance.'
            )
        else:
            self.ssh_private_key_file = os.path.expanduser(
                self.ssh_private_key_file
            )

        if not ip_address:
            raise SSHProviderException(
                'IP address is required to connect to instance.'
            )
        else:
            self.instance_ip = ip_address

        self.ssh_user = (
            ssh_user or
            self._get_value(ssh_user, 'ssh_user')
        )
        if not self.ssh_user:
            raise SSHProviderException(
                'SSH user is required to connect to instance.'
            )

    def _is_instance_running(self):
        """
        Return True.

        Instance must be running with SSh provider.
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

    def _launch_instance(self):
        """
        Do nothing.

        SSH instance must be running.
        """
        raise SSHProviderException(
            'SSH provider cannot launch instances.'
        )

    def _set_image_id(self):
        """
        Do nothing.
        """
        raise SSHProviderException(
            'SSH provider has no access to cloud API.'
        )

    def _set_instance_ip(self):
        """
        Do nothing.
        """
        raise SSHProviderException(
            'SSH provider has no access to cloud API.'
        )

    def _start_instance(self):
        """
        Do nothing.
        """
        raise SSHProviderException(
            'SSH provider has no access to cloud API.'
        )

    def _stop_instance(self):
        """
        Do nothing.
        """
        raise SSHProviderException(
            'SSH provider has no access to cloud API.'
        )

    def _terminate_instance(self):
        """
        Do nothing.
        """
        raise SSHProviderException(
            'SSH provider has no access to cloud API.'
        )
