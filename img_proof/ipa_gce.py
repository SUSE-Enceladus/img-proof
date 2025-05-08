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
from google.auth.exceptions import RefreshError
from google.auth.transport.requests import AuthorizedSession
from google.cloud import compute_v1
from google.api_core.extended_operation import ExtendedOperation


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
        raise GCECloudException(
            'Unable to retrieve {type_name}: {error}'.format(
                type_name=type_name,
                error=str(error)
            )
        ) from error


class GCECloud(IpaCloud):
    """
    Cloud framework class for testing Google Compute Engine (GCE) images.
    """
    cloud = 'gce'

    def post_init(self):
        """Initialize EC2 cloud framework class."""

        self.service_account_file = (
            self.custom_args.get('service_account_file') or
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
        self.image_project = self.custom_args.get('image_project')
        self.architecture = self.custom_args.get(
            'architecture',
            'x86_64'
        ).upper()

        self.use_gvnic = False
        self.sev = None
        self.stack_type = None

        for option in self.instance_options:
            if option == 'GVNIC':
                self.use_gvnic = True
            elif option == 'SEV_SNP_CAPABLE':
                self.sev = 'SEV_SNP'
            elif not self.sev and option == 'SEV_CAPABLE':
                self.sev = 'SEV'
            elif not self.sev and option == 'TDX_CAPABLE':
                self.sev = 'TDX'
            elif "=" in option:
                opt, val = option.split('=')
                if opt == 'STACK_TYPE':
                    self.stack_type = val

        if self.custom_args.get('use_gvnic'):
            self.use_gvnic = True
        if not self.sev and self.custom_args.get('sev_capable', False):
            self.sev = 'SEV'
        if not self.stack_type:
            self.stack_type = 'IPV4_ONLY'

        self.credentials = self._get_credentials()
        self.instances_client = compute_v1.InstancesClient(
            credentials=self.credentials
        )
        self.zone_operations_client = compute_v1.ZoneOperationsClient(
            credentials=self.credentials
        )

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

        try:
            creds = service_account.Credentials.from_service_account_file(
                self.service_account_file
            )
        except Exception as error:
            raise GCECloudException(
                'Could not extract credentials from "{creds_file}": '
                '{error}'.format(
                    creds_file=self.service_account_file,
                    error=error
                )
            )

        try:
            # https://developers.google.com/identity/protocols/oauth2/scopes#google-sign-in
            scoped_credentials = creds.with_scopes(['profile'])
            authed_session = AuthorizedSession(scoped_credentials)
            authed_session.get('https://www.googleapis.com/oauth2/v2/userinfo')
        except RefreshError:
            raise GCECloudException(
                'The provided credentials are invalid or expired: '
                '{creds_file}'.format(
                    creds_file=self.service_account_file
                )
            )
        except Exception as error:
            raise GCECloudException(
                'GCP authentication failed: {error}'.format(error=error)
            )

        return creds

    def _get_instance(self):
        """Retrieve instance matching instance_id."""
        with handle_gce_http_errors('instance', self.running_instance_id):
            instance = self.instances_client.get(
                project=self.service_account_project,
                zone=self.region,
                instance=self.running_instance_id
            )

        return instance

    def _get_ssh_public_key(self):
        """Generate SSH public key from private key."""
        key = ipa_utils.get_public_ssh_key(self.ssh_private_key_file)
        return '{user}:{key}'.format(
            user=self.ssh_user,
            key=key.decode().strip()
        )

    def _get_network(self, network_id):
        """
        Return the network by network id (name).

        If network not found GCE will raise a 404 error.
        """
        networks_client = compute_v1.NetworksClient(
            credentials=self.credentials
        )

        with handle_gce_http_errors('network', network_id):
            network = networks_client.get(
                project=self.service_account_project,
                network=network_id
            )

        return network

    def _get_subnet(self, subnet_id):
        """
        Return the subnet by subnet id (name).

        If subnet not found GCE will raise a 404 error.
        """
        subnetworks_client = compute_v1.SubnetworksClient(
            credentials=self.credentials
        )

        with handle_gce_http_errors('subnet', subnet_id):
            # Subnet lives in a region whereas self.region
            # is a specific zone (us-west1-a).
            region = '-'.join(self.region.split('-')[:-1])
            subnet = subnetworks_client.get(
                project=self.service_account_project,
                region=region,
                subnetwork=subnet_id
            )

        return subnet

    def _get_instance_type(self, type_name):
        """
        Return the instance type by name.

        If type not found GCE will raise a 404 error.
        """
        machine_types_client = compute_v1.MachineTypesClient(
            credentials=self.credentials
        )

        with handle_gce_http_errors('instance type', type_name):
            machine_type = machine_types_client.get(
                project=self.service_account_project,
                zone=self.region,
                machine_type=type_name
            )

        return machine_type

    def _get_image(self, image_name):
        """
        Return the image by image name.

        If image is not found GCE will raise a 404 error.
        """
        images_client = compute_v1.ImagesClient(
            credentials=self.credentials
        )

        with handle_gce_http_errors('image', image_name):
            image = images_client.get(
                project=self.image_project or self.service_account_project,
                image=image_name
            )

        return image

    def _get_disk(self, disk_name):
        """
        Return the disk by name.

        If disk is not found GCE will raise a 404 error.
        """
        disks_client = compute_v1.DisksClient(
            credentials=self.credentials
        )

        with handle_gce_http_errors('disk', disk_name):
            disk = disks_client.get(
                project=self.service_account_project,
                zone=self.region,
                disk=disk_name
            )

        return disk

    def _get_network_config(self, subnet_id, use_gvnic=False):
        """
        Return the network config.

        If a subnet_id is provided use the subnet and
        network. Otherwise use the default network.
        """
        interface = {
            'access_configs': [{
                'name': 'External NAT'
            }],
            'stack_type': self.stack_type
        }

        if use_gvnic:
            interface['nic_type'] = 'GVNIC'

        if subnet_id:
            subnet = self._get_subnet(subnet_id)
            interface['subnetwork'] = subnet.self_link
            interface['network'] = subnet.network.self_link
        else:
            interface['network'] = self._get_network('default').self_link

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
            'enable_secure_boot': enable_secure_boot,
            'enable_vtpm': enable_vtpm,
            'enable_integrity_monitoring': enable_integrity_monitoring
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
        root_disk_size,
        architecture,
        auto_delete=True,
        boot_disk=True,
        disk_type='PERSISTENT',
        disk_mode='READ_WRITE',
        shielded_instance_config=None,
        sev=None,
        use_gvnic=False
    ):
        """Return an instance config for launching a new instance."""
        config = {
            'metadata': {
                'items': [
                    {'key': 'ssh-keys', 'value': ssh_key},
                    {'key': 'enable-guest-attributes', 'value': 'true'}
                ]
            },
            'service_accounts': [{
                'email': service_account_email,
                'scopes': [
                    'https://www.googleapis.com/auth/devstorage.read_only'
                ]
            }],
            'machine_type': machine_type,
            'disks': [{
                'auto_delete': auto_delete,
                'boot': boot_disk,
                'type_': disk_type,
                'mode': disk_mode,
                'device_name': instance_name,
                'initialize_params': {
                    'disk_name': instance_name,
                    'source_image': source_image,
                    'disk_size_gb': root_disk_size,
                    'architecture': architecture
                }
            }],
            'network_interfaces': network_interfaces,
            'name': instance_name
        }

        guest_os_features = []

        if shielded_instance_config:
            config['shielded_instance_config'] = shielded_instance_config
            guest_os_features.append({'type_': 'UEFI_COMPATIBLE'})

        if sev:
            config['confidential_instance_config'] = {
                'confidential_instance_type': sev,
                'enable_confidential_compute': True
            }
            config['scheduling'] = {'on_host_maintenance': 'TERMINATE'}

            if sev == 'SEV_SNP':
                config['min_cpu_platform'] = 'AMD Milan'
                guest_os_features.append({'type_': 'SEV_SNP_CAPABLE'})
            elif sev == 'SEV':
                guest_os_features.append({'type_': 'SEV_CAPABLE'})
            else:
                guest_os_features.append({'type_': 'TDX_CAPABLE'})

        if use_gvnic:
            guest_os_features.append({'type_': 'GVNIC'})

        if guest_os_features:
            config['disks'][0]['guest_os_features'] = guest_os_features

        instance = compute_v1.Instance(
            mapping=config
        )
        return instance

    def _launch_instance(self):
        """Launch an instance of the given image."""
        self.running_instance_id = self._generate_instance_name()
        self.logger.debug('ID of instance: %s' % self.running_instance_id)

        machine_type = self._get_instance_type(
            self.instance_type or GCE_DEFAULT_TYPE
        ).self_link
        source_image = self._get_image(self.image_id).self_link
        network_interfaces = [
            self._get_network_config(self.subnet_id, self.use_gvnic)
        ]

        kwargs = {
            'instance_name': self.running_instance_id,
            'machine_type': machine_type,
            'service_account_email': self.service_account_email,
            'source_image': source_image,
            'ssh_key': self.ssh_public_key,
            'network_interfaces': network_interfaces,
            'sev': self.sev,
            'use_gvnic': self.use_gvnic,
            'root_disk_size': self.root_disk_size,
            'architecture': self.architecture
        }

        if self.enable_uefi:
            kwargs['shielded_instance_config'] = \
                self.get_shielded_instance_config(
                    enable_secure_boot=self.enable_secure_boot
                )

        try:
            request = compute_v1.InsertInstanceRequest(
                project=self.service_account_project,
                zone=self.region,
                instance_resource=self.get_instance_config(**kwargs)
            )
            operation = self.instances_client.insert(request=request)
        except Exception as error:
            raise GCECloudException(
                'Failed to launch instance: {message}'.format(
                    message=str(error)
                )
            ) from error

        self.wait_for_extended_operation(operation, 'instance creation')

        self._wait_on_instance(
            'RUNNING',
            timeout=self.timeout
        )

    def _set_image_id(self):
        """Set the image_id instance variable based on boot disk."""
        instance = self._get_instance()

        for disk_info in instance.disks:
            if disk_info.boot:
                disk_name = disk_info.source.rsplit('/', maxsplit=1)[-1]
                break

        disk = self._get_disk(disk_name)

        # Example sourceImage format:
        # projects/debian-cloud/global/images/opensuse-leap-15.0-YYYYMMDD
        self.image_id = disk.source_image.rsplit('/', maxsplit=1)[-1]

    def _validate_region(self):
        """Validate region was passed in and is a valid GCE zone."""
        if not self.region:
            raise GCECloudException(
                'Zone is required for GCE cloud framework: '
                'Example: us-west1-a'
            )

        zones_client = compute_v1.ZonesClient(
            credentials=self.credentials
        )

        try:
            zone = zones_client.get(
                project=self.service_account_project,
                zone=self.region
            )
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
        return instance.status

    def _is_instance_running(self):
        """Return True if instance is in running state."""
        return self._get_instance_state() == 'RUNNING'

    def _set_instance_ip(self):
        """Retrieve and set the instance ip address."""
        instance = self._get_instance()

        interface = instance.network_interfaces[0]
        try:
            self.instance_ip = interface.access_configs[0].nat_i_p
        except IndexError:
            self.instance_ip = interface.network_i_p

        if not self.instance_ip:
            raise GCECloudException(
                'IP address for instance: %s cannot be found.'
                % self.running_instance_id
            )

    def _start_instance(self):
        """Start the instance."""
        self.instances_client.start(
            project=self.service_account_project,
            zone=self.region,
            instance=self.running_instance_id
        )

        self._wait_on_instance(
            'RUNNING',
            timeout=self.timeout
        )

    def _stop_instance(self):
        """Stop the instance."""
        request = compute_v1.StopInstanceRequest(
            discard_local_ssd=True,
            project=self.service_account_project,
            zone=self.region,
            instance=self.running_instance_id
        )
        self.instances_client.stop(request)

        # In GCE an instance that is stopped has a state of TERMINATED:
        # https://cloud.google.com/compute/docs/instances/instance-life-cycle
        self._wait_on_instance(
            'TERMINATED',
            timeout=self.timeout
        )

    def _terminate_instance(self):
        """Terminate the instance."""
        self.instances_client.delete(
            project=self.service_account_project,
            zone=self.region,
            instance=self.running_instance_id
        )

    def get_console_log(self):
        """
        Return console log output if it is available.
        """
        output = self.instances_client.get_serial_port_output(
            project=self.service_account_project,
            zone=self.region,
            instance=self.running_instance_id
        )
        return output.contents

    def _wait_on_operation(self, operation_name, timeout=600, wait_period=10):
        start = time.time()
        end = start + timeout

        while time.time() < end:
            time.sleep(wait_period)

            operation = self.zone_operations_client.get(
                project=self.service_account_project,
                zone=self.region,
                operation=operation_name
            )

            if operation.status == 'DONE':
                return operation

    def wait_for_extended_operation(
        self,
        operation: ExtendedOperation,
        verbose_name: str = 'operation',
        timeout: int = 300
    ):
        retryable_errors = ('QUOTA_EXCEEDED', 'PRECONDITION_FAILED')
        result = operation.result(timeout=timeout)

        if operation.warnings:
            for warning in operation.warnings:
                self.logger.warning(f'{warning.code}: {warning.message}')

        if operation.error_code:
            if operation.error_code in retryable_errors:
                error_class = IpaRetryableError
            else:
                error_class = GCECloudException

            raise error_class(
                f'Failed to launch instance: {operation.error_code}: '
                f'{operation.error_message}'
            )

        return result
