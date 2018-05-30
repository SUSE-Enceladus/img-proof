# -*- coding: utf-8 -*-

"""Provider module for testing Google Compute Engine (GCE) images."""

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
from ipa.ipa_libcloud import LibcloudProvider

from libcloud.common.google import ResourceNotFoundError
from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver


class GCEProvider(LibcloudProvider):
    """Provider class for testing Google Compute Engine (GCE) images."""

    def __init__(self,
                 access_key_id=None,  # Not used in GCE
                 account_name=None,  # Not used in GCE
                 cleanup=None,
                 config=None,
                 description=None,
                 distro_name=None,
                 early_exit=None,
                 history_log=None,
                 image_id=None,
                 inject=None,
                 instance_type=None,
                 log_level=30,
                 no_default_test_dirs=False,
                 provider_config=None,
                 region=None,
                 results_dir=None,
                 root_device_size=None,
                 root_device_type=None,
                 running_instance_id=None,
                 secret_access_key=None,  # Not used in GCE
                 service_account_file=None,
                 ssh_key_name=None,  # Not used in GCE
                 ssh_private_key=None,
                 ssh_user=None,
                 subnet_id=None,
                 test_dirs=None,
                 test_files=None,
                 vnet_name=None,  # Not used in GCE
                 vnet_resource_group=None  # Not used in GCE
                 ):
        super(GCEProvider, self).__init__('gce',
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
                                          root_device_size,
                                          root_device_type,
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
        self.subnet_id = subnet_id

        self._get_service_account_info()
        self.compute_driver = self._get_driver()

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

    def _get_disk_config(self):
        """
        Return a list of dictionary disk configurations.

        Contains the root device config for instance.
        """
        disk_type = self._get_disk_type()
        image = self._get_image()

        disk_config = [{
            'autoDelete': True,
            'boot': True,
            'type': 'PERSISTENT',
            'mode': 'READ_WRITE',
            'deviceName': self.running_instance_id,
            'initializeParams': {
                'diskName': self.running_instance_id,
                'diskSizeGb': self.root_device_size or 10,
                'diskType': disk_type.extra['selfLink'],
                'sourceImage': image.extra['selfLink']
            }
        }]

        return disk_config

    def _get_disk_type(self):
        """Return the disk type object based on name."""
        try:
            disk_type = self.compute_driver.ex_get_disktype(
                self.root_device_type or 'pd-standard',
                zone=self.region
            )
        except Exception as error:
            raise GCEProviderException(
                'Unable to locate disk device type: {0}.'.format(error)
            )

        return disk_type

    def _get_image(self):
        """Return the image type object based on image id."""
        try:
            image = self.compute_driver.ex_get_image(self.image_id)
        except Exception as error:
            raise GCEProviderException(
                'Unable to locate image type: {0}.'.format(error)
            )

        return image

    def _get_instance(self):
        """Retrieve instance matching instance_id."""
        try:
            instance = self.compute_driver.ex_get_node(
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

    def _get_ssh_public_key(self):
        """Generate SSH public key from private key."""
        key = ipa_utils.generate_public_ssh_key(self.ssh_private_key)
        return '{user}:{key} {user}'.format(
            user=self.ssh_user,
            key=key.decode()
        )

    def _get_subnet(self, subnet_id):
        subnet = None
        try:
            # Subnet lives in a region whereas self.region
            # is a specific zone (us-west1-a).
            region = '-'.join(self.region.split('-')[:-1])
            subnet = self.compute_driver.ex_get_subnetwork(
                subnet_id, region=region
            )
        except Exception:
            raise GCEProviderException(
                'GCE subnet: {subnet_id} not found.'.format(
                    subnet_id=subnet_id
                )
            )

        return subnet

    def _launch_instance(self):
        """Launch an instance of the given image."""
        if not self.region:
            raise GCEProviderException(
                'Zone is required to launch a new GCE instance. '
                'Example: us-west1-a'
            )

        metadata = {'key': 'ssh-keys', 'value': self.ssh_public_key}
        self.running_instance_id = ipa_utils.generate_instance_name(
            'gce-ipa-test'
        )

        kwargs = {
            'location': self.region,
            'ex_metadata': metadata,
            'ex_disks_gce_struct': self._get_disk_config(),
        }

        if self.subnet_id:
            kwargs['ex_subnetwork'] = self._get_subnet(self.subnet_id)
            kwargs['ex_network'] = kwargs['ex_subnetwork'].network

        try:
            instance = self.compute_driver.create_node(
                self.running_instance_id,
                self.instance_type or GCE_DEFAULT_TYPE,
                self.image_id,
                **kwargs
            )
        except ResourceNotFoundError as error:
            try:
                message = error.value['message']
            except TypeError:
                message = error

            raise GCEProviderException(
                'An error occurred launching instance: {message}.'.format(
                    message=message
                )
            )

        self.compute_driver.wait_until_running([instance])

    def _set_image_id(self):
        """If existing image used get image id."""
        instance = self._get_instance()
        self.image_id = instance.image
