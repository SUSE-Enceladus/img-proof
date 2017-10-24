# -*- coding: utf-8 -*-

"""Provider module for testing AWS EC2 images."""

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

from ipa import ipa_utils
from ipa.ipa_constants import (
    EC2_CONFIG_FILE,
    EC2_DEFAULT_TYPE,
    EC2_DEFAULT_USER
)
from ipa.ipa_exceptions import EC2ProviderException
from ipa.ipa_libcloud import LibcloudProvider

from libcloud.common.exceptions import BaseHTTPError
from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver


class EC2Provider(LibcloudProvider):
    """Provider class for testing AWS EC2 images."""

    def __init__(self,
                 access_key_id=None,
                 account_name=None,
                 cleanup=None,
                 config=None,
                 desc=None,
                 distro_name=None,
                 early_exit=None,
                 history_log=None,
                 image_id=None,
                 instance_type=None,
                 log_level=30,
                 no_default_test_dirs=False,
                 provider_config=None,
                 region=None,
                 results_dir=None,
                 running_instance_id=None,
                 secret_access_key=None,
                 service_account_file=None,  # Not used in EC2
                 ssh_key_name=None,
                 ssh_private_key=None,
                 ssh_user=None,
                 storage_container=None,  # Not used in EC2
                 test_dirs=None,
                 test_files=None):
        """Initialize EC2 provider class."""
        super(EC2Provider, self).__init__('EC2',
                                          cleanup,
                                          config,
                                          desc,
                                          distro_name,
                                          early_exit,
                                          history_log,
                                          image_id,
                                          instance_type,
                                          log_level,
                                          no_default_test_dirs,
                                          provider_config,
                                          region,
                                          results_dir,
                                          running_instance_id,
                                          test_dirs,
                                          test_files)
        config_file = self.provider_config or EC2_CONFIG_FILE

        if not account_name:
            raise EC2ProviderException(
                'Account required for config file: %s' % config_file
            )

        if not self.region:
            raise EC2ProviderException(
                'Region is required to connect to EC2.'
            )

        self.account_name = account_name
        self.ec2_config = ipa_utils.get_config(config_file)
        self.logger.debug(
            'Using EC2 config file: %s' % config_file
        )

        self.access_key_id = (
            access_key_id or
            self._get_from_ec2_config('access_key_id')
        )
        self.secret_access_key = (
            secret_access_key or
            self._get_from_ec2_config('secret_access_key')
        )
        self.ssh_key_name = (
            ssh_key_name or
            self._get_from_ec2_config('ssh_key_name')
        )
        self.ssh_private_key = (
            ssh_private_key or
            self._get_from_ec2_config('ssh_private_key')
        )
        self.ssh_user = (
            ssh_user or
            self._get_from_ec2_config('user') or
            EC2_DEFAULT_USER
        )

        if not self.ssh_private_key:
            raise EC2ProviderException(
                'SSH private key file is required to connect to instance.'
            )

        self.compute_driver = self._get_driver()

    def _get_driver(self):
        """Get authenticated EC2 driver."""
        ComputeEngine = get_driver(Provider.EC2)
        return ComputeEngine(
            self.access_key_id,
            self.secret_access_key,
            region=self.region
        )

    def _get_from_ec2_config(self, entry):
        """Get config entry from ec2utils config file."""
        return ipa_utils.get_from_config(
            self.ec2_config,
            ''.join(['region-', self.region]),
            ''.join(['account-', self.account_name]),
            entry
        )

    def _get_instance(self):
        """Retrieve instance matching instance_id."""
        try:
            instance = self.compute_driver.list_nodes(
                ex_node_ids=[self.running_instance_id]
            )[0]
        except (IndexError, BaseHTTPError):
            raise EC2ProviderException(
                'Instance with ID: {instance_id} not found.'.format(
                    instance_id=self.running_instance_id
                )
            )
        return instance

    def _launch_instance(self):
        """Launch an instance of the given image."""
        if not self.ssh_key_name:
            raise EC2ProviderException(
                'SSH Key Name is required to launch an EC2 instance.'
            )

        instance = self.compute_driver.create_node(
            name=ipa_utils.generate_instance_name('ec2-ipa-test'),
            size=self._get_instance_size(EC2_DEFAULT_TYPE),
            image=self._get_image(),
            ex_keyname=self.ssh_key_name
        )
        self.compute_driver.wait_until_running([instance])
        self.running_instance_id = instance.id

    def _set_image_id(self):
        """If existing image used get image id."""
        instance = self._get_instance()
        self.image_id = instance.extra['image_id']
