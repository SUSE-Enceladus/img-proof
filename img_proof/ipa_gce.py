# -*- coding: utf-8 -*-

"""Cloud framework module for testing Google Compute Engine (GCE) images."""

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

import json
import os

from img_proof import ipa_utils
from img_proof.ipa_constants import (
    GCE_DEFAULT_TYPE,
    GCE_DEFAULT_USER
)
from img_proof.ipa_exceptions import GCECloudException
from img_proof.ipa_cloud import IpaCloud

from libcloud.common.google import ResourceNotFoundError
from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver


class GCECloud(IpaCloud):
    """
    Cloud framework class for testing Google Compute Engine (GCE) images.
    """

    def __init__(
        self,
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
        cloud_config=None,
        region=None,
        results_dir=None,
        running_instance_id=None,
        service_account_file=None,
        ssh_private_key_file=None,
        ssh_user=None,
        subnet_id=None,
        test_dirs=None,
        test_files=None,
        timeout=None,
        collect_vm_info=None
    ):
        super(GCECloud, self).__init__(
            'gce',
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

        self.service_account_file = (
            service_account_file or
            self.ipa_config['service_account_file']
        )
        if not self.service_account_file:
            raise GCECloudException(
                'Service account file is required to connect to GCE.'
            )
        else:
            self.service_account_file = os.path.expanduser(
                self.service_account_file
            )

        if not self.ssh_private_key_file:
            raise GCECloudException(
                'SSH private key file is required to connect to instance.'
            )

        self.ssh_user = self.ssh_user or GCE_DEFAULT_USER
        self.ssh_public_key = self._get_ssh_public_key()

        self._get_service_account_info()
        self.compute_driver = self._get_driver()

        self._validate_region()

    def _get_service_account_info(self):
        """Retrieve json dict from service account file."""
        with open(self.service_account_file, 'r') as f:
            info = json.load(f)

        self.service_account_email = info.get('client_email')
        if not self.service_account_email:
            raise GCECloudException(
                'Service account JSON file is invalid for GCE. '
                'client_email key is expected. See getting started '
                'docs for information on GCE configuration.'
            )

        self.service_account_project = info.get('project_id')
        if not self.service_account_project:
            raise GCECloudException(
                'Service account JSON file is invalid for GCE. '
                'project_id key is expected. See getting started '
                'docs for information on GCE configuration.'
            )

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
            instance = self.compute_driver.ex_get_node(
                self.running_instance_id,
                zone=self.region
            )
        except ResourceNotFoundError as e:
            raise GCECloudException(
                'Instance with id: {id} cannot be found: {error}'.format(
                    id=self.running_instance_id, error=e
                )
            )

        return instance

    def _get_ssh_public_key(self):
        """Generate SSH public key from private key."""
        key = ipa_utils.generate_public_ssh_key(self.ssh_private_key_file)
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
            raise GCECloudException(
                'GCE subnet: {subnet_id} not found.'.format(
                    subnet_id=subnet_id
                )
            )

        return subnet

    def _launch_instance(self):
        """Launch an instance of the given image."""
        metadata = {'key': 'ssh-keys', 'value': self.ssh_public_key}
        self.running_instance_id = ipa_utils.generate_instance_name(
            'gce-img-proof-test'
        )
        self.logger.debug('ID of instance: %s' % self.running_instance_id)

        kwargs = {
            'location': self.region,
            'ex_metadata': metadata,
            'ex_service_accounts': [{
                'email': self.service_account_email,
                'scopes': ['storage-ro']
            }]
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

            raise GCECloudException(
                'An error occurred launching instance: {message}.'.format(
                    message=message
                )
            )

        self.compute_driver.wait_until_running(
            [instance],
            timeout=self.timeout
        )

    def _set_image_id(self):
        """If existing image used get image id."""
        instance = self._get_instance()
        self.image_id = instance.image

    def _validate_region(self):
        """Validate region was passed in and is a valid GCE zone."""
        if not self.region:
            raise GCECloudException(
                'Zone is required for GCE cloud framework: '
                'Example: us-west1-a'
            )

        try:
            zone = self.compute_driver.ex_get_zone(self.region)
        except Exception:
            zone = None

        if not zone:
            raise GCECloudException(
                '{region} is not a valid GCE zone. '
                'Example: us-west1-a'.format(
                    region=self.region
                )
            )

    def _get_instance_state(self):
        """Attempt to retrieve the state of the instance."""
        instance = self._get_instance()
        return instance.state

    def _is_instance_running(self):
        """Return True if instance is in running state."""
        return self._get_instance_state() == 'running'

    def _set_instance_ip(self):
        """Retrieve and set the instance ip address."""
        instance = self._get_instance()

        if instance.public_ips:
            self.instance_ip = instance.public_ips[0]
        elif instance.private_ips:
            self.instance_ip = instance.private_ips[0]
        else:
            raise GCECloudException(
                'IP address for instance: %s cannot be found.'
                % self.running_instance_id
            )

    def _start_instance(self):
        """Start the instance."""
        instance = self._get_instance()
        self.compute_driver.ex_start_node(instance)
        self.compute_driver.wait_until_running(
            [instance],
            timeout=self.timeout
        )

    def _stop_instance(self):
        """Stop the instance."""
        instance = self._get_instance()
        self.compute_driver.ex_stop_node(instance)
        self._wait_on_instance('stopped', timeout=self.timeout)

    def _terminate_instance(self):
        """Terminate the instance."""
        instance = self._get_instance()
        instance.destroy()
