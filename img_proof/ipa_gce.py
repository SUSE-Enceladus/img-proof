# -*- coding: utf-8 -*-

"""Cloud framework module for testing Google Compute Engine (GCE) images."""

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
import time

from contextlib import contextmanager, suppress

from img_proof import ipa_utils
from img_proof.ipa_constants import (
    GCE_DEFAULT_TYPE,
    GCE_DEFAULT_USER
)
from img_proof.ipa_exceptions import GCECloudException, IpaRetryableError
from img_proof.ipa_cloud import IpaCloud

from google.oauth2 import service_account
from googleapiclient import discovery


def get_message_from_http_error(error, resource_name):
    """
    Attempt to parse error message from json.

    If there is an error getting the message content
    use the default of `resource not found`.
    """
    with suppress(AttributeError):
        # In python 3.5 content is bytes
        error.content = error.content.decode()

    try:
        message = json.loads(error.content)['error']['message']
    except (AttributeError, KeyError):
        message = 'Resource {resource_name} not found.'.format(
            resource_name=resource_name
        )

    return message


@contextmanager
def handle_gce_http_errors(type_name, resource_name):
    """
    Context manager to handle GCE HTTP Errors.
    """
    try:
        yield
    except Exception as error:
        message = get_message_from_http_error(error, resource_name)

        raise GCECloudException(
            'Unable to retrieve {type_name}: {error}'.format(
                type_name=type_name,
                error=message
            )
        ) from error


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
        log_level=None,
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
        collect_vm_info=None,
        image_project=None,
        enable_secure_boot=None,
        enable_uefi=None
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
            subnet_id,
            enable_secure_boot,
            enable_uefi
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
        self.image_project = image_project

        self.credentials = self._get_credentials()
        self.compute_driver = self._get_driver()

        self._validate_region()

    def _get_credentials(self):
        """Retrieve credentials object using service account file."""
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

        return service_account.Credentials.from_service_account_file(
            self.service_account_file
        )

    def _get_driver(self):
        """Get authenticated GCE driver."""
        return discovery.build(
            'compute',
            'v1',
            credentials=self.credentials,
            cache_discovery=False
        )

    def _get_instance(self):
        """Retrieve instance matching instance_id."""
        with handle_gce_http_errors('instance', self.running_instance_id):
            instance = self.compute_driver.instances().get(
                project=self.service_account_project,
                zone=self.region,
                instance=self.running_instance_id
            ).execute()

        return instance

    def _get_ssh_public_key(self):
        """Generate SSH public key from private key."""
        key = ipa_utils.get_public_ssh_key(self.ssh_private_key_file)
        return '{user}:{key} {user}'.format(
            user=self.ssh_user,
            key=key.decode()
        )

    def _get_network(self, network_id):
        """
        Return the network by network id (name).

        If network not found GCE will raise a 404 error.
        """
        with handle_gce_http_errors('network', network_id):
            network = self.compute_driver.networks().get(
                project=self.service_account_project,
                network=network_id
            ).execute()

        return network

    def _get_subnet(self, subnet_id):
        """
        Return the subnet by subnet id (name).

        If subnet not found GCE will raise a 404 error.
        """
        with handle_gce_http_errors('subnet', subnet_id):
            # Subnet lives in a region whereas self.region
            # is a specific zone (us-west1-a).
            region = '-'.join(self.region.split('-')[:-1])
            subnet = self.compute_driver.subnetworks().get(
                project=self.service_account_project,
                region=region,
                subnetwork=subnet_id
            ).execute()

        return subnet

    def _get_instance_type(self, type_name):
        """
        Return the instance type by name.

        If type not found GCE will raise a 404 error.
        """
        with handle_gce_http_errors('instance type', type_name):
            machine_type = self.compute_driver.machineTypes().get(
                project=self.service_account_project,
                zone=self.region,
                machineType=type_name
            ).execute()

        return machine_type

    def _get_image(self, image_name):
        """
        Return the image by image name.

        If image is not found GCE will raise a 404 error.
        """
        with handle_gce_http_errors('image', image_name):
            image = self.compute_driver.images().get(
                project=self.image_project or self.service_account_project,
                image=image_name
            ).execute()

        return image

    def _get_disk(self, disk_name):
        """
        Return the disk by name.

        If disk is not found GCE will raise a 404 error.
        """
        with handle_gce_http_errors('disk', disk_name):
            disk = self.compute_driver.disks().get(
                project=self.service_account_project,
                zone=self.region,
                disk=disk_name
            ).execute()

        return disk

    def _get_network_config(self, subnet_id):
        """
        Return the network config.

        If a subnet_id is provided use the subnet and
        network. Otherwise use the default network.
        """
        interface = {
            'accessConfigs': [{
                'name': 'External NAT',
                'type': 'ONE_TO_ONE_NAT'
            }]
        }

        if subnet_id:
            subnet = self._get_subnet(subnet_id)
            interface['subnetwork'] = subnet['selfLink']
            interface['network'] = subnet['network']
        else:
            interface['network'] = self._get_network('default')['selfLink']

        return interface

    @staticmethod
    def get_shielded_instance_config(
        enable_secure_boot=False,
        enable_vtpm=True,
        enable_integrity_monitoring=True
    ):
        """
        Return shielded instance config object.

        Return with default values unless overridden by args.
        """
        shielded_instance_config = {
            'enableSecureBoot': enable_secure_boot,
            'enableVtpm': enable_vtpm,
            'enableIntegrityMonitoring': enable_integrity_monitoring
        }

        return shielded_instance_config

    @staticmethod
    def get_instance_config(
        instance_name,
        machine_type,
        network_interfaces,
        service_account_email,
        source_image,
        ssh_key,
        auto_delete=True,
        boot_disk=True,
        disk_type='PERSISTENT',
        disk_mode='READ_WRITE',
        shielded_instance_config=None,
    ):
        """Return an instance config for launching a new instance."""
        config = {
            'metadata': {
                'items': [
                    {'key': 'ssh-keys', 'value': ssh_key},
                    {'key': 'enable-guest-attributes', 'value': True}
                ]
            },
            'serviceAccounts': [{
                'email': service_account_email,
                'scopes': [
                    'https://www.googleapis.com/auth/devstorage.read_only'
                ]
            }],
            'machineType': machine_type,
            'disks': [{
                'autoDelete': auto_delete,
                'boot': boot_disk,
                'type': disk_type,
                'mode': disk_mode,
                'deviceName': instance_name,
                'initializeParams': {
                    'diskName': instance_name,
                    'sourceImage': source_image
                }
            }],
            'networkInterfaces': network_interfaces,
            'name': instance_name
        }

        if shielded_instance_config:
            config['shieldedInstanceConfig'] = shielded_instance_config
            config['disks'][0]['guestOsFeatures'] = [{
                'type': 'UEFI_COMPATIBLE'
            }]

        return config

    def _launch_instance(self):
        """Launch an instance of the given image."""
        self.running_instance_id = ipa_utils.generate_instance_name(
            'gce-img-proof-test'
        )
        self.logger.debug('ID of instance: %s' % self.running_instance_id)

        machine_type = self._get_instance_type(
            self.instance_type or GCE_DEFAULT_TYPE
        )['selfLink']
        source_image = self._get_image(self.image_id)['selfLink']
        network_interfaces = [self._get_network_config(self.subnet_id)]

        kwargs = {
            'instance_name': self.running_instance_id,
            'machine_type': machine_type,
            'service_account_email': self.service_account_email,
            'source_image': source_image,
            'ssh_key': self.ssh_public_key,
            'network_interfaces': network_interfaces
        }

        if self.enable_uefi:
            kwargs['shielded_instance_config'] = \
                self.get_shielded_instance_config(
                    enable_secure_boot=self.enable_secure_boot
                )

        try:
            response = self.compute_driver.instances().insert(
                project=self.service_account_project,
                zone=self.region,
                body=self.get_instance_config(**kwargs)
            ).execute()
        except Exception as error:
            with suppress(AttributeError):
                # In python 3.5 content is bytes
                error.content = error.content.decode()

            error_obj = json.loads(error.content)['error']

            try:
                message = error_obj['message']
            except (AttributeError, KeyError):
                message = 'Unknown exception.'

            if error_obj['code'] == 412:
                # 412 is conditionNotmet
                error_class = IpaRetryableError
            else:
                error_class = GCECloudException

            raise error_class(
                'Failed to launch instance: {message}'.format(
                    message=message
                )
            ) from error

        operation = self._wait_on_operation(response['name'])

        if 'error' in operation and operation['error'].get('errors'):
            error = operation['error']['errors'][0]

            if error['code'] in ('QUOTA_EXCEEDED', 'PRECONDITION_FAILED'):
                error_class = IpaRetryableError
            else:
                error_class = GCECloudException

            raise error_class(
                'Failed to launch instance: {message}'.format(
                    message=error['message']
                )
            )

        self._wait_on_instance(
            'RUNNING',
            timeout=self.timeout
        )

    def _set_image_id(self):
        """Set the image_id instance variable based on boot disk."""
        instance = self._get_instance()

        for disk_info in instance['disks']:
            if disk_info.get('boot'):
                disk_name = disk_info['source'].rsplit('/', maxsplit=1)[-1]
                break

        disk = self._get_disk(disk_name)

        # Example sourceImage format:
        # projects/debian-cloud/global/images/opensuse-leap-15.0-YYYYMMDD
        self.image_id = disk['sourceImage'].rsplit('/', maxsplit=1)[-1]

    def _validate_region(self):
        """Validate region was passed in and is a valid GCE zone."""
        if not self.region:
            raise GCECloudException(
                'Zone is required for GCE cloud framework: '
                'Example: us-west1-a'
            )

        try:
            zone = self.compute_driver.zones().get(
                project=self.service_account_project,
                zone=self.region
            ).execute()
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
        return instance['status']

    def _is_instance_running(self):
        """Return True if instance is in running state."""
        return self._get_instance_state() == 'RUNNING'

    def _set_instance_ip(self):
        """Retrieve and set the instance ip address."""
        instance = self._get_instance()

        interface = instance['networkInterfaces'][0]
        try:
            self.instance_ip = interface['accessConfigs'][0]['natIP']
        except (KeyError, IndexError):
            try:
                self.instance_ip = interface['networkIP']
            except KeyError:
                raise GCECloudException(
                    'IP address for instance: %s cannot be found.'
                    % self.running_instance_id
                )

    def _start_instance(self):
        """Start the instance."""
        self.compute_driver.instances().start(
            project=self.service_account_project,
            zone=self.region,
            instance=self.running_instance_id
        ).execute()

        self._wait_on_instance(
            'RUNNING',
            timeout=self.timeout
        )

    def _stop_instance(self):
        """Stop the instance."""
        self.compute_driver.instances().stop(
            project=self.service_account_project,
            zone=self.region,
            instance=self.running_instance_id
        ).execute()

        # In GCE an instance that is stopped has a state of TERMINATED:
        # https://cloud.google.com/compute/docs/instances/instance-life-cycle
        self._wait_on_instance(
            'TERMINATED',
            timeout=self.timeout
        )

    def _terminate_instance(self):
        """Terminate the instance."""
        self.compute_driver.instances().delete(
            project=self.service_account_project,
            zone=self.region,
            instance=self.running_instance_id
        ).execute()

    def get_console_log(self):
        """
        Return console log output if it is available.
        """
        output = self.compute_driver.instances().getSerialPortOutput(
            project=self.service_account_project,
            zone=self.region,
            instance=self.running_instance_id
        ).execute()
        return output.get('contents', '')

    def _wait_on_operation(self, operation_name, timeout=600, wait_period=10):
        start = time.time()
        end = start + timeout

        while time.time() < end:
            time.sleep(wait_period)

            operation = self.compute_driver.zoneOperations().get(
                project=self.service_account_project,
                zone=self.region,
                operation=operation_name
            ).execute()

            if operation['status'] == 'DONE':
                return operation
