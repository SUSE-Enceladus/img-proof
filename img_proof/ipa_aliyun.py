# -*- coding: utf-8 -*-

"""Cloud framework module for testing Aliyun images."""

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

import json
import os

from collections import ChainMap, defaultdict
from base64 import b64decode, b64encode

from aliyunsdkcore.client import AcsClient
from aliyunsdkecs.request.v20140526.DescribeInstancesRequest import (
    DescribeInstancesRequest
)
from aliyunsdkecs.request.v20140526.StartInstanceRequest import (
    StartInstanceRequest
)
from aliyunsdkecs.request.v20140526.StopInstanceRequest import (
    StopInstanceRequest
)
from aliyunsdkecs.request.v20140526.DeleteInstanceRequest import (
    DeleteInstanceRequest
)
from aliyunsdkecs.request.v20140526.GetInstanceConsoleOutputRequest import (
    GetInstanceConsoleOutputRequest
)
from aliyunsdkecs.request.v20140526.RunInstancesRequest import (
    RunInstancesRequest
)

from img_proof.ipa_constants import (
    ALIYUN_DEFAULT_TYPE,
    ALIYUN_DEFAULT_USER
)
from img_proof.ipa_exceptions import AliyunCloudException
from img_proof.ipa_cloud import IpaCloud


class AliyunCloud(IpaCloud):
    """Cloud framework class for testing Aliyun images."""
    cloud = 'aliyun'

    def post_init(self):
        """Initialize Aliyun cloud framework class."""

        # Get command line values that are not None
        cmd_line_values = self._get_non_null_values(self.custom_args)

        self.ipa_config = defaultdict(
            lambda: None,
            ChainMap(cmd_line_values, self.ipa_config)
        )

        if not self.region:
            raise AliyunCloudException(
                'Region is required to connect to Aliyun.'
            )

        self.access_key = self.ipa_config['access_key']
        if not self.access_key:
            raise AliyunCloudException(
                'Access key is required to connect to Aliyun.'
            )

        self.access_secret = self.ipa_config['access_secret']
        if not self.access_secret:
            raise AliyunCloudException(
                'Access secret is required to connect to Aliyun.'
            )

        self.ssh_private_key_file = self.ipa_config['ssh_private_key_file']
        if not self.ssh_private_key_file:
            raise AliyunCloudException(
                'SSH private key file is required to connect to instance.'
            )
        else:
            self.ssh_private_key_file = os.path.expanduser(
                self.ssh_private_key_file
            )

        self.security_group_id = self.ipa_config['security_group_id']
        self.v_switch_id = self.ipa_config['v_switch_id']

        # Possible formats:
        # cn-beijing or cn-beijing-a
        # ap-northeast-1 or ap-northeast-1a
        self.zone = None
        region_split = self.region.split('-')

        if len(region_split) == 3 and self.region[-1].isalpha():
            self.zone = self.region

            if region_split[-1] == self.region[-1]:
                # cn-beijing-a
                self.region = self.region[:-2]
            else:
                # ap-northeast-1a
                self.region = self.region[:-1]

        self.ssh_key_name = self.ipa_config['ssh_key_name']

        self.ssh_user = (
            cmd_line_values.get('ssh_user') or
            self.ipa_config.get('ssh_user') or
            ALIYUN_DEFAULT_USER
        )

    def _connect(self):
        """Connect to aliyun compute client."""
        try:
            client = AcsClient(
                self.access_key,
                self.access_secret,
                self.region
            )
        except Exception:
            raise AliyunCloudException(
                'Could not connect to region: %s' % self.region
            )
        return client

    def _get_instance(self):
        """Retrieve instance matching instance_id."""
        client = self._connect()

        request = DescribeInstancesRequest()
        request.set_accept_format('json')
        request.set_InstanceIds(json.dumps([self.running_instance_id]))

        try:
            response = json.loads(client.do_action_with_exception(request))
            instance = response['Instances']['Instance'][0]
        except Exception:
            raise AliyunCloudException(
                'Instance with ID: {instance_id} not found.'.format(
                    instance_id=self.running_instance_id
                )
            )
        return instance

    def _get_instance_state(self):
        """
        Attempt to retrieve the state of the instance.

        Raises:
            AliyunCloudException: If the instance cannot be found.
        """
        instance = self._get_instance()
        state = None

        try:
            state = instance['Status']
        except KeyError:
            raise AliyunCloudException(
                'Status of instance with id: {instance_id}, '
                'cannot be found.'.format(
                    instance_id=self.running_instance_id
                )
            )

        return state

    def _is_instance_running(self):
        """
        Return True if instance is in running state.
        """
        return self._get_instance_state() == 'Running'

    def _launch_instance(self):
        """Launch an instance of the given image."""
        client = self._connect()
        instance_name = self._generate_instance_name()

        request = RunInstancesRequest()
        request.set_InstanceType(self.instance_type or ALIYUN_DEFAULT_TYPE)
        request.set_InstanceChargeType('PostPaid')
        request.set_ImageId(self.image_id)
        request.set_InstanceName(instance_name)
        request.set_Amount(1)
        request.set_InternetMaxBandwidthOut(5)
        request.set_SystemDiskSize(self.root_disk_size)
        request.set_IoOptimized('optimized')
        request.set_SecurityEnhancementStrategy('Active')
        request.set_VSwitchId(self.v_switch_id)
        request.set_SecurityGroupId(self.security_group_id)

        if self.zone:
            request.set_ZoneId(self.zone)

        if self.ssh_key_name:
            request.set_KeyPairName(self.ssh_key_name)
        else:
            request.set_UserData(b64encode(self._get_user_data().encode()))

        try:
            response = json.loads(client.do_action_with_exception(request))
        except Exception as error:
            raise AliyunCloudException(
                'Unable to create instance: {0}.'.format(error)
            )

        self.running_instance_id = \
            response['InstanceIdSets']['InstanceIdSet'][0]
        self.logger.debug('ID of instance: %s' % self.running_instance_id)
        self._wait_on_instance('Running', self.timeout)

    def _set_image_id(self):
        """If existing image used get image id."""
        instance = self._get_instance()
        self.image_id = instance['ImageId']

    def _set_instance_ip(self):
        """
        Retrieve instance ip and cache it.

        Current preference is for public then private.
        """
        instance = self._get_instance()

        public_ip = next(iter(instance['PublicIpAddress']['IpAddress']), None)
        private_ip = next(iter(instance['InnerIpAddress']['IpAddress']), None)
        self.instance_ip = public_ip or private_ip

        if not self.instance_ip:
            raise AliyunCloudException(
                'IP address for instance cannot be found.'
            )

    def _start_instance(self):
        """Start the instance."""
        client = self._connect()

        request = StartInstanceRequest()
        request.set_accept_format('json')
        request.set_InstanceId(self.running_instance_id)

        client.do_action_with_exception(request)
        self._wait_on_instance('Running', self.timeout)

    def _stop_instance(self):
        """Stop the instance."""
        client = self._connect()

        request = StopInstanceRequest()
        request.set_accept_format('json')
        request.set_InstanceId(self.running_instance_id)

        client.do_action_with_exception(request)
        self._wait_on_instance('Stopped', self.timeout)

    def _terminate_instance(self):
        """Terminate the instance."""
        client = self._connect()

        request = DeleteInstanceRequest()
        request.set_accept_format('json')
        request.set_Force(True)
        request.set_InstanceId(self.running_instance_id)

        client.do_action_with_exception(request)

    def get_console_log(self):
        """
        Return console log output if it is available.
        """
        client = self._connect()

        request = GetInstanceConsoleOutputRequest()
        request.set_accept_format('json')
        request.set_InstanceId(self.running_instance_id)

        response = json.loads(client.do_action_with_exception(request))
        output = b64decode(response['ConsoleOutput'])

        return output.decode()
