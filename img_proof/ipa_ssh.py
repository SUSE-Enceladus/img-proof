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

    def __init__(
        self,
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
        cloud_config=None,
        region=None,  # Not used in SSH
        results_dir=None,
        running_instance_id=None,  # Not used in SSH
        ssh_private_key_file=None,
        ssh_user=None,
        subnet_id=None,  # Not used in SSH
        test_dirs=None,
        test_files=None,
        timeout=None,
        collect_vm_info=None
    ):
        """Initialize Azure cloud class."""
        super(SSHCloud, self).__init__(
            'ssh',
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
            cloud_config,
            region,
            results_dir,
            running_instance_id,
            test_dirs,
            test_files,
            timeout,
            collect_vm_info,
            ssh_private_key_file,
            ssh_user,
            subnet_id
        )

        # Cannot cleanup SSH instance
        self.cleanup = False

        if not ip_address:
            raise SSHCloudException(
                'IP address is required to connect to instance.'
            )
        else:
            self.instance_ip = ip_address

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
