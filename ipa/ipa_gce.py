# -*- coding: utf-8 -*-

"""Provider module for testing Google Cloud Compute images."""

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

import json
import os

from ipa import ipa_utils
from ipa.ipa_constants import (
    GCE_DEFAULT_TYPE,
    GCE_DEFAULT_USER
)
from ipa.ipa_exceptions import GCEProviderException
from ipa.ipa_provider import IpaProvider

from libcloud.common.google import ResourceNotFoundError
from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver


class GCEProvider(IpaProvider):
    """Provider class for testing Google Cloud Compute images."""

    def __init__(self,
                 access_key_id=None,  # Not used in GCE
                 account_name=None,  # Not used in GCE
                 cleanup=None,
                 config=None,
                 desc=None,
                 distro_name=None,
                 early_exit=None,
                 history_log=None,
                 image_id=None,
                 instance_type=None,
                 log_level=30,
                 provider_config=None,
                 region=None,
                 results_dir=None,
                 running_instance_id=None,
                 secret_access_key=None,  # Not used in GCE
                 service_account_file=None,
                 ssh_key_name=None,  # Not used in GCE
                 ssh_private_key=None,
                 ssh_user=None,
                 storage_container=None,  # Not used in GCE
                 test_dirs=None,
                 test_files=None):
        super(GCEProvider, self).__init__('GCE',
                                          cleanup,
                                          config,
                                          desc,
                                          distro_name,
                                          early_exit,
                                          history_log,
                                          image_id,
                                          instance_type,
                                          log_level,
                                          provider_config,
                                          region,
                                          results_dir,
                                          running_instance_id,
                                          test_dirs,
                                          test_files)
        self.service_account_file = (
            service_account_file or
            self._get_value(
                service_account_file,
                config_key='service_account_file'
            )
        )
        if not self.service_account_file:
            raise GCEProviderException(
                'Service account file is required to connect to GCE.'
            )
        else:
            self.service_account_file = os.path.expanduser(
                self.service_account_file
            )

        self.ssh_private_key = (
            ssh_private_key or
            self._get_value(ssh_private_key, config_key='ssh_private_key')
        )
        if not self.ssh_private_key:
            raise GCEProviderException(
                'SSH private key file is required to connect to instance.'
            )
        else:
            self.ssh_private_key = os.path.expanduser(
                self.ssh_private_key
            )

        self.ssh_user = (
            ssh_user or
            GCE_DEFAULT_USER
        )

        self.ssh_public_key = self._get_ssh_public_key()
        self._get_service_account_info()
        self.gce_driver = self._get_driver()

    def _get_service_account_info(self):
        """Retrieve json dict from service account file."""
        with open(self.service_account_file, 'r') as f:
            info = json.load(f)

        self.service_account_email = info['client_email']
        self.service_account_project = info['project_id']

    def _get_driver(self):
        """Get authenticated GCE driver."""
        ComputeEngine = get_driver(Provider.GCE)
        return ComputeEngine(
            self.service_account_email,
            self.service_account_file,
            project=self.service_account_project
        )

    def _get_instance(self):
        """Retrieve instance matching instance_id."""
        try:
            instance = self.gce_driver.ex_get_node(
                self.running_instance_id,
                zone=self.region
            )
        except ResourceNotFoundError as e:
            raise GCEProviderException(
                'Instance with id: {id} cannot be found: {error}'.format(
                    id=self.running_instance_id, error=e
                )
            )

        return instance

    def _get_instance_state(self):
        """Attempt to retrieve the state of the instance."""
        instance = self._get_instance()
        return instance.state

    def _get_ssh_public_key(self):
        """Generate SSH public key from private key."""
        key = ipa_utils.generate_public_ssh_key(self.ssh_private_key)
        return '{user}:{key} {user}'.format(
            user=self.ssh_user,
            key=key.decode()
        )

    def _is_instance_running(self):
        """Return True if instance is in running state."""
        return self._get_instance_state() == 'running'

    def _launch_instance(self):
        """Launch an instance of the given image."""
        if not self.region:
            raise GCEProviderException(
                'Zone (region) is required to launch a new GCE instance.'
            )

        metadata = {'key': 'ssh-keys', 'value': self.ssh_public_key}
        self.running_instance_id = ipa_utils.generate_instance_name(
            'gce-ipa-test'
        )

        instance = self.gce_driver.create_node(
            self.running_instance_id,
            self.instance_type or GCE_DEFAULT_TYPE,
            self.image_id,
            self.region,
            ex_metadata=metadata
        )
        self.gce_driver.wait_until_running([instance])

    def _set_image_id(self):
        """If existing image used get image id."""
        instance = self._get_instance()
        self.image_id = instance.image

    def _set_instance_ip(self):
        """Retrieve and set the instance ip address."""
        instance = self._get_instance()

        try:
            self.instance_ip = instance.public_ips[0]
        except IndexError:
            raise GCEProviderException(
                'IP address for instance: %s cannot be found.'
                % self.running_instance_id
            )

    def _start_instance(self):
        """Start the instance."""
        instance = self._get_instance()
        self.gce_driver.ex_start_node(instance)
        self.gce_driver.wait_until_running([instance])

    def _stop_instance(self):
        """Stop the instance."""
        instance = self._get_instance()
        self.gce_driver.ex_stop_node(instance)

    def _terminate_instance(self):
        """Terminate the instance."""
        instance = self._get_instance()
        instance.destroy()
