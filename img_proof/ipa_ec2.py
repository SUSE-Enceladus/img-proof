# -*- coding: utf-8 -*-

"""Cloud framework module for testing AWS EC2 images."""

# Copyright (c) 2020 SUSE LLC. All rights reserved.
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

import boto3
import os
import time

from collections import ChainMap, defaultdict

from img_proof import ipa_utils
from img_proof.ipa_constants import (
    EC2_CONFIG_FILE,
    EC2_DEFAULT_TYPE,
    EC2_DEFAULT_USER
)
from img_proof.ipa_exceptions import EC2CloudException
from img_proof.ipa_cloud import IpaCloud


class EC2Cloud(IpaCloud):
    """Cloud framework class for testing AWS EC2 images."""
    cloud = 'ec2'

    def post_init(self):
        """Initialize EC2 cloud framework class."""

        # Get command line values that are not None
        cmd_line_values = self._get_non_null_values(self.custom_args)

        self.zone = None
        self.account_name = self.custom_args.get('account_name')

        if not self.account_name:
            self.logger.debug(
                'No account provided. To use the EC2 config file an '
                'account name is required.'
            )

        if not self.region:
            raise EC2CloudException(
                'Region is required to connect to EC2.'
            )
        elif self.region[-1].isalpha():
            self.zone = self.region
            self.region = self.region[:-1]

        config_file = self.cloud_config or EC2_CONFIG_FILE

        ec2_config = {}
        try:
            ec2_config = ipa_utils.get_config_values(
                config_file,
                ''.join(['region-', self.region]),
                ''.join(['account-', self.account_name])
            )
            self.logger.debug(
                'Using EC2 config file: %s' % config_file
            )
        except Exception:
            self.logger.debug(
                'EC2 config file not found: %s' % config_file
            )

        self.ec2_config = defaultdict(
            lambda: None,
            ChainMap(cmd_line_values, ec2_config, self.ipa_config)
        )

        self.access_key_id = self.ec2_config['access_key_id']
        self.secret_access_key = self.ec2_config['secret_access_key']
        self.security_group_id = self.ec2_config['security_group_id']
        self.ssh_key_name = self.ec2_config['ssh_key_name']
        self.additional_info = self.ec2_config['additional_info']
        self.subnet_id = self.ec2_config['subnet_id']

        self.ssh_user = (
            cmd_line_values.get('ssh_user') or
            ec2_config.get('user') or
            self.ipa_config.get('ssh_user') or
            EC2_DEFAULT_USER
        )

        self.ssh_private_key_file = (
            cmd_line_values.get('ssh_private_key_file') or
            ec2_config.get('ssh_private_key') or
            self.ipa_config.get('ssh_private_key_file')
        )

        if not self.ssh_private_key_file:
            raise EC2CloudException(
                'SSH private key file is required to connect to instance.'
            )
        else:
            self.ssh_private_key_file = os.path.expanduser(
                self.ssh_private_key_file
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
            raise EC2CloudException(
                'Could not connect to region: %s' % self.region
            )
        return resource

    def _get_instance(self):
        """Retrieve instance matching instance_id."""
        resource = self._connect()

        try:
            instance = resource.Instance(self.running_instance_id)
        except Exception:
            raise EC2CloudException(
                'Instance with ID: {instance_id} not found.'.format(
                    instance_id=self.running_instance_id
                )
            )
        return instance

    def _get_image(self):
        """Retrieve image matching image_id."""
        resource = self._connect()

        try:
            image = resource.Image(self.image_id)
        except Exception:
            raise EC2CloudException(
                'Image with ID: {image_id} not found.'.format(
                    image_id=self.image_id
                )
            )
        return image

    def _get_instance_state(self):
        """
        Attempt to retrieve the state of the instance.
         Raises:
            EC2CloudException: If the instance cannot be found.
        """
        instance = self._get_instance()
        state = None

        try:
            state = instance.state['Name']
        except Exception:
            raise EC2CloudException(
                'Instance with id: {instance_id}, '
                'cannot be found.'.format(
                    instance_id=self.running_instance_id
                )
            )

        return state

    def _is_instance_running(self):
        """
        Return True if instance is in running state.
        """
        return self._get_instance_state() == 'running'

    def _launch_instance(self):
        """Launch an instance of the given image."""
        resource = self._connect()

        image = self._get_image()
        instance_name = self._generate_instance_name()
        kwargs = {
            'InstanceType': self.instance_type or EC2_DEFAULT_TYPE,
            'ImageId': self.image_id,
            'MaxCount': 1,
            'MinCount': 1,
            'BlockDeviceMappings': [{
                'DeviceName': image.root_device_name,
                'Ebs': {'VolumeSize': self.root_disk_size}
            }],
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

        if self.zone:
            kwargs['Placement'] = {'AvailabilityZone': self.zone}

        if self.ssh_key_name:
            kwargs['KeyName'] = self.ssh_key_name
        else:
            kwargs['UserData'] = self._get_user_data()

        if self.subnet_id:
            kwargs['SubnetId'] = self.subnet_id

        if self.security_group_id:
            kwargs['SecurityGroupIds'] = [self.security_group_id]

        if self.additional_info:
            kwargs['AdditionalInfo'] = self.additional_info

        cpu_options = self.custom_args.get('cpu_options', {})
        for option in self.instance_options:
            try:
                # AmdSevSnp=enabled
                key, value = option.split('=')
            except ValueError:
                self.logger.warning(f'Invalid CPU option provided: {option}')

            try:
                # CpuOptions=AmdSevSnp.enabled
                opt_key, opt_val = value.split('.')
            except ValueError:
                opt_key = None

            if opt_key and key.lower() == 'cpuoptions':
                cpu_options[opt_key] = opt_val
            elif opt_key and key.lower() != 'cpuoptions':
                pass  # No other options supported at the moment
            else:
                cpu_options[key] = value

        if cpu_options:
            kwargs['CpuOptions'] = cpu_options

        try:
            instances = resource.create_instances(**kwargs)
        except Exception as error:
            raise EC2CloudException(
                'Unable to create instance: {0}.'.format(error)
            )

        self.running_instance_id = instances[0].instance_id
        self.logger.debug('ID of instance: %s' % self.running_instance_id)
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
        except (IndexError, TypeError):
            ipv6 = None

        self.instance_ip = instance.public_ip_address or \
            ipv6 or instance.private_ip_address

        if not self.instance_ip:
            raise EC2CloudException(
                'IP address for instance cannot be found.'
            )

    def _start_instance(self):
        """Start the instance."""
        kwargs = {}

        if self.additional_info:
            kwargs['AdditionalInfo'] = self.additional_info

        instance = self._get_instance()
        instance.start(**kwargs)

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

    def get_console_log(self):
        """
        Return console log output if it is available.

        Boto3 will return a response with no output if serial console
        is not available.
        """
        instance = self._get_instance()

        start = time.time()
        end = start + 300

        while time.time() < end:
            response = instance.console_output()

            if 'Output' in response:
                return response['Output']

            time.sleep(10)

        return ''
