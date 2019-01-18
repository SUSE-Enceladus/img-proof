# -*- coding: utf-8 -*-

"""Provider module for testing AWS EC2 images."""

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

import boto3

from ipa import ipa_utils
from ipa.ipa_constants import (
    BASH_SSH_SCRIPT,
    EC2_CONFIG_FILE,
    EC2_DEFAULT_TYPE,
    EC2_DEFAULT_USER
)
from ipa.ipa_exceptions import IpaException, EC2ProviderException
from ipa.ipa_provider import IpaProvider


class EC2Provider(IpaProvider):
    """Provider class for testing AWS EC2 images."""

    def __init__(self,
                 accelerated_networking=None,  # Not used in EC2
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
                 ip_address=None,  # Not used in EC2
                 log_level=30,
                 no_default_test_dirs=False,
                 provider_config=None,
                 region=None,
                 results_dir=None,
                 running_instance_id=None,
                 secret_access_key=None,
                 security_group_id=None,
                 service_account_file=None,  # Not used in EC2
                 ssh_key_name=None,
                 ssh_private_key_file=None,
                 ssh_user=None,
                 subnet_id=None,
                 test_dirs=None,
                 test_files=None,
                 timeout=None,
                 vnet_name=None,  # Not used in EC2
                 vnet_resource_group=None,  # Not used in EC2
                 collect_vm_info=None):
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
                                          running_instance_id,
                                          test_dirs,
                                          test_files,
                                          timeout,
                                          collect_vm_info)
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
        self.security_group_id = (
            security_group_id or
            self._get_value(
                security_group_id, 'security_group_id'
            )
        )
        self.ssh_key_name = (
            ssh_key_name or
            self._get_from_ec2_config('ssh_key_name')
        )
        self.ssh_private_key_file = (
            ssh_private_key_file or
            self._get_from_ec2_config('ssh_private_key') or
            self._get_value(
                ssh_private_key_file, 'ssh_private_key_file'
            )
        )
        self.ssh_user = (
            ssh_user or
            self._get_from_ec2_config('user') or
            EC2_DEFAULT_USER
        )
        self.subnet_id = subnet_id

        if not self.ssh_private_key_file:
            raise EC2ProviderException(
                'SSH private key file is required to connect to instance.'
            )

    def _connect(self):
        """Connect to ec2 resource."""
        resource = None
        try:
            resource = boto3.resource(
                'ec2',
                aws_access_key_id=self.access_key_id,
                aws_secret_access_key=self.secret_access_key,
                region_name=self.region
            )
            # boto3 resource is lazy so attempt method to test connection
            resource.meta.client.describe_account_attributes()
        except Exception:
            raise EC2ProviderException(
                'Could not connect to region: %s' % self.region
            )
        return resource

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

    def _get_instance(self):
        """Retrieve instance matching instance_id."""
        resource = self._connect()

        try:
            instance = resource.Instance(self.running_instance_id)
        except Exception:
            raise EC2ProviderException(
                'Instance with ID: {instance_id} not found.'.format(
                    instance_id=self.running_instance_id
                )
            )
        return instance

    def _get_instance_state(self):
        """
        Attempt to retrieve the state of the instance.
         Raises:
            EC2ProviderException: If the instance cannot be found.
        """
        instance = self._get_instance()
        state = None

        try:
            state = instance.state['Name']
        except Exception:
            raise EC2ProviderException(
                'Instance with id: {instance_id}, '
                'cannot be found.'.format(
                    instance_id=self.running_instance_id
                )
            )

        return state

    def _get_user_data(self):
        """
        Return formatted bash script string.

        The public ssh key is added by cloud init to the instance based on
        the ssh user and private key file.
        """
        key = ipa_utils.generate_public_ssh_key(
            self.ssh_private_key_file
        ).decode()
        script = BASH_SSH_SCRIPT.format(user=self.ssh_user, key=key)
        return script

    def _is_instance_running(self):
        """
        Return True if instance is in running state.
        """
        return self._get_instance_state() == 'running'

    def _launch_instance(self):
        """Launch an instance of the given image."""
        resource = self._connect()

        instance_name = ipa_utils.generate_instance_name('ec2-ipa-test')
        kwargs = {
            'InstanceType': self.instance_type or EC2_DEFAULT_TYPE,
            'ImageId': self.image_id,
            'MaxCount': 1,
            'MinCount': 1,
            'TagSpecifications': [
                {
                    'ResourceType': 'instance',
                    'Tags': [
                        {
                            'Key': 'Name',
                            'Value': instance_name
                        }
                    ]
                }
            ]
        }

        if self.ssh_key_name:
            kwargs['KeyName'] = self.ssh_key_name
        else:
            kwargs['UserData'] = self._get_user_data()

        if self.subnet_id:
            kwargs['SubnetId'] = self.subnet_id

        if self.security_group_id:
            kwargs['SecurityGroupIds'] = [self.security_group_id]

        try:
            instances = resource.create_instances(**kwargs)
        except Exception as error:
            raise EC2ProviderException(
                'Unable to create instance: {0}.'.format(error)
            )

        self.running_instance_id = instances[0].instance_id
        self._wait_on_instance('running', self.timeout)

    def _set_image_id(self):
        """If existing image used get image id."""
        instance = self._get_instance()
        self.image_id = instance.image_id

    def _set_instance_ip(self):
        """
        Retrieve instance ip and cache it.

        Current preference is for public ipv4, ipv6 and private.
        """
        instance = self._get_instance()

        # ipv6
        try:
            ipv6 = instance.network_interfaces[0].ipv6_addresses[0]
        except IndexError:
            ipv6 = None

        self.instance_ip = instance.public_ip_address or \
            ipv6 or instance.private_ip_address

        if not self.instance_ip:
            raise EC2ProviderException(
                'IP address for instance cannot be found.'
            )

    def _start_instance(self):
        """Start the instance."""
        instance = self._get_instance()
        instance.start()
        self._wait_on_instance('running', self.timeout)

    def _stop_instance(self):
        """Stop the instance."""
        instance = self._get_instance()
        instance.stop()
        self._wait_on_instance('stopped', self.timeout)

    def _terminate_instance(self):
        """Terminate the instance."""
        instance = self._get_instance()
        instance.terminate()
