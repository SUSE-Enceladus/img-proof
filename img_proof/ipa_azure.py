# -*- coding: utf-8 -*-

"""Module for testing instances in Azure."""

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

import os

from azure.common.client_factory import get_client_from_auth_file
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.compute import ComputeManagementClient

from img_proof import ipa_utils
from img_proof.ipa_constants import AZURE_DEFAULT_TYPE, AZURE_DEFAULT_USER
from img_proof.ipa_exceptions import AzureCloudException
from img_proof.ipa_cloud import IpaCloud


class AzureCloud(IpaCloud):
    """Class for testing instances in Azure."""

    def __init__(
        self,
        accelerated_networking=False,
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
        vnet_name=None,
        vnet_resource_group=None,
        collect_vm_info=None,
        enable_secure_boot=None,
        enable_uefi=None
    ):
        """Initialize Azure Cloud class."""
        super(AzureCloud, self).__init__(
            'azure',
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

        self.vnet_name = vnet_name or self.ipa_config['vnet_name']
        self.vnet_resource_group = (
                vnet_resource_group or self.ipa_config['vnet_resource_group']
        )

        subnet_args = [
            self.subnet_id, self.vnet_name, self.vnet_resource_group
        ]
        if any(subnet_args) and not all(subnet_args):
            raise AzureCloudException(
                'subnet_id, vnet_resource_group and vnet_name'
                ' are all required to use an existing subnet.'
            )

        self.service_account_file = (
            service_account_file or self.ipa_config['service_account_file']
        )
        if not self.service_account_file:
            raise AzureCloudException(
                'Service account file is required to connect to Azure.'
            )
        else:
            self.service_account_file = os.path.expanduser(
                self.service_account_file
            )

        if not self.ssh_private_key_file:
            raise AzureCloudException(
                'SSH private key file is required to connect to instance.'
            )

        self.accelerated_networking = (
            accelerated_networking or
            self.ipa_config['accelerated_networking']
        )
        self.ssh_user = self.ssh_user or AZURE_DEFAULT_USER
        self.ssh_public_key = self._get_ssh_public_key()

        self.compute = self._get_management_client(ComputeManagementClient)
        self.network = self._get_management_client(NetworkManagementClient)
        self.resource = self._get_management_client(ResourceManagementClient)

        if self.running_instance_id:
            self._set_default_resource_names()

    def _create_network_interface(
        self, ip_config_name, nic_name, public_ip, region,
        resource_group_name, subnet, accelerated_networking=False
    ):
        """
        Create a network interface in the resource group.

        Attach NIC to the subnet and public IP provided.
        """
        nic_config = {
            'location': region,
            'ip_configurations': [{
                'name': ip_config_name,
                'private_ip_allocation_method': 'Dynamic',
                'subnet': {
                    'id': subnet.id
                },
                'public_ip_address': {
                    'id': public_ip.id
                },
            }]
        }

        if accelerated_networking:
            nic_config['enable_accelerated_networking'] = True

        try:
            nic_setup = self.network.network_interfaces.create_or_update(
                resource_group_name, nic_name, nic_config
            )
        except Exception as error:
            raise AzureCloudException(
                'Unable to create network interface: {0}.'.format(
                    error
                )
            )

        return nic_setup.result()

    def _create_public_ip(self, public_ip_name, resource_group_name, region):
        """
        Create dynamic public IP address in the resource group.
        """
        public_ip_config = {
            'location': region,
            'public_ip_allocation_method': 'Dynamic'
        }

        try:
            public_ip_setup = \
                self.network.public_ip_addresses.create_or_update(
                    resource_group_name, public_ip_name, public_ip_config
                )
        except Exception as error:
            raise AzureCloudException(
                'Unable to create public IP: {0}.'.format(error)
            )

        return public_ip_setup.result()

    def _create_resource_group(self, region, resource_group_name):
        """
        Create resource group if it does not exist.
        """
        resource_group_config = {'location': region}

        try:
            self.resource.resource_groups.create_or_update(
                resource_group_name, resource_group_config
            )
        except Exception as error:
            raise AzureCloudException(
                'Unable to create resource group: {0}.'.format(error)
            )

    def _create_storage_profile(self):
        """
        Create the storage profile for the instance.

        Image reference can be a custom image name or a published urn.
        """
        if self.image_publisher:
            storage_profile = {
                'image_reference': {
                    'publisher': self.image_publisher,
                    'offer': self.image_offer,
                    'sku': self.image_sku,
                    'version': self.image_version
                },
            }
        else:
            for image in self.compute.images.list():
                if image.name == self.image_id:
                    image_id = image.id
                    break
            else:
                raise AzureCloudException(
                    'Image with name {0} not found.'.format(self.image_id)
                )

            storage_profile = {
                'image_reference': {
                    'id': image_id
                }
            }

        return storage_profile

    def _create_subnet(self, resource_group_name, subnet_id, vnet_name):
        """
        Create a subnet in the provided vnet and resource group.
        """
        subnet_config = {'address_prefix': '10.0.0.0/29'}

        try:
            subnet_setup = self.network.subnets.create_or_update(
                resource_group_name, vnet_name, subnet_id, subnet_config
            )
        except Exception as error:
            raise AzureCloudException(
                'Unable to create subnet: {0}.'.format(error)
            )

        return subnet_setup.result()

    def _create_virtual_network(self, region, resource_group_name, vnet_name):
        """
        Create a vnet in the given resource group with default address space.
        """
        vnet_config = {
            'location': region,
            'address_space': {
                'address_prefixes': ['10.0.0.0/27']
            }
        }

        try:
            vnet_setup = self.network.virtual_networks.create_or_update(
                resource_group_name, vnet_name, vnet_config
            )
        except Exception as error:
            raise AzureCloudException(
                'Unable to create vnet: {0}.'.format(error)
            )

        vnet_setup.wait()

    def _create_vm(self, vm_config):
        """
        Attempt to create or update VM instance based on vm_parameters config.
        """
        try:
            vm_setup = self.compute.virtual_machines.create_or_update(
                self.running_instance_id, self.running_instance_id,
                vm_config
            )
        except Exception as error:
            raise AzureCloudException(
                'An exception occurred creating virtual machine: {0}'.format(
                    error
                )
            )

        vm_setup.wait()

    def _create_vm_config(self, interface):
        """
        Create the VM config dictionary.

        Requires an existing network interface object.
        """
        # Split image ID into it's components.
        self._process_image_id()

        hardware_profile = {
            'vm_size': self.instance_type or AZURE_DEFAULT_TYPE
        }

        network_profile = {
            'network_interfaces': [{
                'id': interface.id,
                'primary': True
            }]
        }

        storage_profile = self._create_storage_profile()

        os_profile = {
            'computer_name': self.running_instance_id,
            'admin_username': self.ssh_user,
            'linux_configuration': {
                'disable_password_authentication': True,
                'ssh': {
                    'public_keys': [{
                        'path': '/home/{0}/.ssh/authorized_keys'.format(
                            self.ssh_user
                        ),
                        'key_data': self.ssh_public_key
                    }]
                }
            }
        }

        vm_config = {
            'location': self.region,
            'os_profile': os_profile,
            'hardware_profile': hardware_profile,
            'storage_profile': storage_profile,
            'network_profile': network_profile
        }

        return vm_config

    def _get_instance(self):
        """
        Return the instance matching the running_instance_id.
        """
        try:
            instance = self.compute.virtual_machines.get(
                self.running_instance_id, self.running_instance_id,
                expand='instanceView'
            )
        except Exception as error:
            raise AzureCloudException(
                'Unable to retrieve instance: {0}'.format(error)
            )

        return instance

    def _get_instance_state(self):
        """
        Retrieve state of instance.
        """
        instance = self._get_instance()
        statuses = instance.instance_view.statuses

        for status in statuses:
            if status.code.startswith('PowerState'):
                return status.display_status

    def _get_management_client(self, client_class):
        """
        Return instance of resource management client.
        """
        try:
            client = get_client_from_auth_file(
                client_class, auth_path=self.service_account_file
            )
        except ValueError as error:
            raise AzureCloudException(
                'Service account file format is invalid: {0}.'.format(error)
            )
        except KeyError as error:
            raise AzureCloudException(
                'Service account file missing key: {0}.'.format(error)
            )
        except Exception as error:
            raise AzureCloudException(
                'Unable to create resource management client: '
                '{0}.'.format(error)
            )

        return client

    def _get_ssh_public_key(self):
        """
        Generate SSH public key from private key.
        """
        key = ipa_utils.get_public_ssh_key(self.ssh_private_key_file)
        return key.decode()

    def _is_instance_running(self):
        """
        Return True if instance is in running state.
        """
        return self._get_instance_state() == 'VM running'

    def _launch_instance(self):
        """
        Create new test instance in a resource group with the same name.
        """
        self.running_instance_id = ipa_utils.generate_instance_name(
            'azure-img-proof-test'
        )
        self.logger.debug('ID of instance: %s' % self.running_instance_id)
        self._set_default_resource_names()

        try:
            # Try block acts as a transaction. If an exception is raised
            # attempt to cleanup the resource group and all created resources.

            # Create resource group.
            self._create_resource_group(self.region, self.running_instance_id)

            if self.subnet_id:
                # Use existing vnet/subnet.
                subnet = self.network.subnets.get(
                    self.vnet_resource_group, self.vnet_name, self.subnet_id
                )
            else:
                self.subnet_id = ''.join([self.running_instance_id, '-subnet'])
                self.vnet_name = ''.join([self.running_instance_id, '-vnet'])

                # Create new vnet
                self._create_virtual_network(
                    self.region, self.running_instance_id, self.vnet_name
                )

                # Create new subnet in new vnet
                subnet = self._create_subnet(
                    self.running_instance_id, self.subnet_id, self.vnet_name
                )

            # Setup interface and public ip in resource group.
            public_ip = self._create_public_ip(
                self.public_ip_name, self.running_instance_id, self.region
            )
            interface = self._create_network_interface(
                self.ip_config_name, self.nic_name, public_ip, self.region,
                self.running_instance_id, subnet, self.accelerated_networking
            )

            # Get dictionary of VM parameters and create instance.
            vm_config = self._create_vm_config(interface)
            self._create_vm(vm_config)
        except Exception:
            try:
                self._terminate_instance()
            except Exception:
                pass
            raise
        else:
            # Ensure VM is in the running state.
            self._wait_on_instance('VM running', timeout=self.timeout)

    def _process_image_id(self):
        """
        Split image id into component values.

        Example: SUSE:SLES:12-SP3:2018.01.04
                 Publisher:Offer:Sku:Version

        Raises:
            If image_id is not a valid format.
        """
        try:
            image_info = self.image_id.strip().split(':')
            self.image_publisher = image_info[0]
            self.image_offer = image_info[1]
            self.image_sku = image_info[2]
            self.image_version = image_info[3]
        except Exception:
            self.image_publisher = None

    def _set_default_resource_names(self):
        """
        Generate names for resources based on the running_instance_id.
        """
        self.ip_config_name = ''.join([
            self.running_instance_id, '-ip-config'
        ])
        self.nic_name = ''.join([self.running_instance_id, '-nic'])
        self.public_ip_name = ''.join([self.running_instance_id, '-public-ip'])

    def _set_image_id(self):
        """
        If an existing instance is used get image id from deployment.
        """
        instance = self._get_instance()
        image_info = instance.storage_profile.image_reference

        if image_info.publisher:
            self.image_id = ':'.join([
                image_info.publisher, image_info.offer,
                image_info.sku, image_info.version
            ])
        else:
            self.image_id = image_info.id.rsplit('/', maxsplit=1)[1]

    def _set_instance_ip(self):
        """
        Get the IP address based on instance ID.

        If public IP address not found attempt to get private IP.
        """
        try:
            ip_address = self.network.public_ip_addresses.get(
                self.running_instance_id, self.public_ip_name
            ).ip_address
        except Exception:
            try:
                ip_address = self.network.network_interfaces.get(
                    self.running_instance_id, self.nic_name
                ).ip_configurations[0].private_ip_address
            except Exception as error:
                raise AzureCloudException(
                    'Unable to retrieve instance IP address: {0}.'.format(
                        error
                    )
                )

        self.instance_ip = ip_address

    def _start_instance(self):
        """
        Start the instance.
        """
        try:
            vm_start = self.compute.virtual_machines.start(
                self.running_instance_id, self.running_instance_id
            )
        except Exception as error:
            raise AzureCloudException(
                'Unable to start instance: {0}.'.format(error)
            )

        vm_start.wait()

    def _stop_instance(self):
        """
        Stop the instance.
        """
        try:
            vm_stop = self.compute.virtual_machines.power_off(
                self.running_instance_id, self.running_instance_id
            )
        except Exception as error:
            raise AzureCloudException(
                'Unable to stop instance: {0}.'.format(error)
            )

        vm_stop.wait()

    def _terminate_instance(self):
        """
        Terminate the resource group and instance.
        """
        try:
            self.resource.resource_groups.delete(self.running_instance_id)
        except Exception as error:
            raise AzureCloudException(
                'Unable to terminate resource group: {0}.'.format(error)
            )

    def get_console_log(self):
        """
        Return console log output if it is available.

        Currently there is no way to get console log from API.
        """
        return ''
