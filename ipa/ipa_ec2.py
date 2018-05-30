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
    BASH_SSH_SCRIPT,
    EC2_CONFIG_FILE,
    EC2_DEFAULT_TYPE,
    EC2_DEFAULT_USER
)
from ipa.ipa_exceptions import IpaException, EC2ProviderException
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
                 secret_access_key=None,
                 service_account_file=None,  # Not used in EC2
                 ssh_key_name=None,
                 ssh_private_key=None,
                 ssh_user=None,
                 subnet_id=None,
                 test_dirs=None,
                 test_files=None,
                 vnet_name=None,  # Not used in EC2
                 vnet_resource_group=None  # Not used in EC2
                 ):
        """Initialize EC2 provider class."""
        super(EC2Provider, self).__init__('ec2',
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
        self.account_name = account_name

        if not self.account_name:
            self.logger.debug(
                'No account provided. To use the EC2 config file an '
                'account name is required.'
            )

        config_file = self.provider_config or EC2_CONFIG_FILE

        if not self.region:
            raise EC2ProviderException(
                'Region is required to connect to EC2.'
            )

        try:
            self.ec2_config = ipa_utils.get_config(config_file)
            self.logger.debug(
                'Using EC2 config file: %s' % config_file
            )
        except IpaException:
            self.ec2_config = None
            self.logger.debug(
                'EC2 config file not found: %s' % config_file
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
            self._get_from_ec2_config('ssh_private_key') or
            self._get_value(ssh_private_key, config_key='ssh_private_key')
        )
        self.ssh_user = (
            ssh_user or
            self._get_from_ec2_config('user') or
            EC2_DEFAULT_USER
        )
        self.subnet_id = subnet_id

        if not self.ssh_private_key:
            raise EC2ProviderException(
                'SSH private key file is required to connect to instance.'
            )

        self.compute_driver = self._get_driver()

    def _get_driver(self):
        """Get authenticated EC2 driver."""
        if not self.access_key_id:
            raise EC2ProviderException(
                'Access key id is required to authenticate EC2 driver.'
            )

        if not self.secret_access_key:
            raise EC2ProviderException(
                'Secret access key is required to authenticate EC2 driver.'
            )

        ComputeEngine = get_driver(Provider.EC2)
        return ComputeEngine(
            self.access_key_id,
            self.secret_access_key,
            region=self.region
        )

    def _get_from_ec2_config(self, entry):
        """Get config entry from ec2utils config file."""
        if self.ec2_config and self.account_name:
            return ipa_utils.get_from_config(
                self.ec2_config,
                ''.join(['region-', self.region]),
                ''.join(['account-', self.account_name]),
                entry
            )
        else:
            return None

    def _get_image(self):
        """Retrieve NodeImage given the image id."""
        try:
            image = self.compute_driver.list_images(
                ex_image_ids=[self.image_id]
            )[0]
        except (IndexError, BaseHTTPError):
            raise EC2ProviderException(
                'Image with ID: {image_id} not found.'.format(
                    image_id=self.image_id
                )
            )

        return image

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

    def _get_instance_size(self):
        """Retrieve NodeSize given the instance type."""
        instance_type = self.instance_type or EC2_DEFAULT_TYPE

        try:
            sizes = self.compute_driver.list_sizes()
            size = [size for size in sizes if size.id == instance_type][0]
        except IndexError:
            raise EC2ProviderException(
                'Instance type: {instance_type} not found.'.format(
                    instance_type=instance_type
                )
            )

        return size

    def _get_subnet(self, subnet_id):
        subnet = None
        try:
            subnet = self.compute_driver.ex_list_subnets(
                subnet_ids=[subnet_id]
            )[0]
        except Exception:
            raise EC2ProviderException(
                'EC2 subnet: {subnet_id} not found.'.format(
                    subnet_id=subnet_id
                )
            )

        return subnet

    def _get_user_data(self):
        """
        Return formatted bash script string.

        The public ssh key is added by cloud init to the instance based on
        the ssh user and private key file.
        """
        key = ipa_utils.generate_public_ssh_key(self.ssh_private_key).decode()
        script = BASH_SSH_SCRIPT.format(user=self.ssh_user, key=key)
        return script

    def _launch_instance(self):
        """Launch an instance of the given image."""
        kwargs = {
            'name': ipa_utils.generate_instance_name('ec2-ipa-test'),
            'size': self._get_instance_size(),
            'image': self._get_image(),
            'ex_blockdevicemappings': [
                {
                    'DeviceName': '/dev/sda1',
                    'Ebs': {
                        'VolumeSize': self.root_device_size or 10,
                        'VolumeType': self.root_device_type or 'gp2'
                    }
                }
            ]
        }

        if self.ssh_key_name:
            kwargs['ex_keyname'] = self.ssh_key_name
        else:
            kwargs['ex_userdata'] = self._get_user_data()

        if self.subnet_id:
            kwargs['ex_subnet'] = self._get_subnet(self.subnet_id)

        instance = self.compute_driver.create_node(**kwargs)

        self.compute_driver.wait_until_running([instance])
        self.running_instance_id = instance.id

    def _set_image_id(self):
        """If existing image used get image id."""
        instance = self._get_instance()
        self.image_id = instance.extra['image_id']
