# -*- coding: utf-8 -*-

"""Provider module for testing AWS EC2 images."""

# Copyright (c) 2017 SUSE LLC
#
# This file is part of ipa.
#
# See LICENSE for license information.

import boto3

from ipa import ipa_utils
from ipa.ipa_constants import (
    EC2_CONFIG_FILE,
    EC2_DEFAULT_TYPE,
    EC2_DEFAULT_USER
)
from ipa.ipa_exceptions import EC2ProviderException
from ipa.ipa_provider import IpaProvider


class EC2Provider(IpaProvider):
    """Provider class for testing AWS EC2 images."""

    def __init__(self,
                 access_key_id=None,
                 account_name=None,
                 cleanup=None,
                 config=None,
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
                 secret_access_key=None,
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
        except:
            raise EC2ProviderException(
                'Could not connect to region: %s' % self.region
            )

        return resource

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
        resource = self._connect()
        return resource.Instance(self.running_instance_id)

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
        except:
            raise EC2ProviderException(
                'Instance with id: {instance_id}, '
                'cannot be found.'.format(
                    instance_id=self.running_instance_id
                )
            )
        return state

    def _is_instance_running(self):
        """Return True if instance is in running state."""
        return self._get_instance_state() == 'running'

    def _launch_instance(self):
        """Launch an instance of the given image."""
        if not self.ssh_key_name:
            raise EC2ProviderException(
                'SSH Key Name is required to launch an EC2 instance.'
            )

        resource = self._connect()
        instances = resource.create_instances(
            ImageId=self.image_id,
            MinCount=1,
            MaxCount=1,
            KeyName=self.ssh_key_name,
            InstanceType=self.instance_type or EC2_DEFAULT_TYPE,
        )

        instances[0].wait_until_running()
        self.running_instance_id = instances[0].instance_id

    def _set_image_id(self):
        """If existing image used get image id from boto3."""
        instance = self._get_instance()
        self.image_id = instance.image_id

    def _set_instance_ip(self):
        """
        Get instance ip of instance.

        Current prefrence is for ipv4.
        """
        instance = self._get_instance()
        if instance.public_ip_address:
            self.instance_ip = instance.public_ip_address
        else:
            try:
                self.instance_ip = \
                        instance.network_interfaces[0].ipv6_addresses[0]
            except IndexError:
                raise EC2ProviderException(
                    'IP address for instance cannot be found.'
                )

    def _start_instance(self):
        """Start the instance."""
        instance = self._get_instance()
        instance.start()
        instance.wait_until_running()

    def _stop_instance(self):
        """Stop the instance."""
        instance = self._get_instance()
        instance.stop()
        instance.wait_until_stopped()

    def _terminate_instance(self):
        """Terminate the instance."""
        instance = self._get_instance()
        instance.terminate()
