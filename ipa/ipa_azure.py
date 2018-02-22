# -*- coding: utf-8 -*-

"""Module for testing instances in Azure."""

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

import json
import os

from azure.common.credentials import ServicePrincipalCredentials
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.compute import ComputeManagementClient

from ipa import ipa_utils
from ipa.ipa_constants import AZURE_DEFAULT_TYPE, AZURE_DEFAULT_USER
from ipa.ipa_exceptions import AzureProviderException
from ipa.ipa_provider import IpaProvider


class AzureProvider(IpaProvider):
    """Class for testing instances in Azure."""

    def __init__(self,
                 access_key_id=None,  # Not used in Azure
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
                 secret_access_key=None,  # Not used in Azure
                 service_account_file=None,  # Not used in Azure
                 ssh_key_name=None,  # Not used in Azure
                 ssh_private_key=None,
                 ssh_user=None,
                 subscription_id=None,
                 subnet_id=None,  # Not used in Azure
                 test_dirs=None,
                 test_files=None):
        """Initialize Azure Provider class."""
        super(AzureProvider, self).__init__('azure',
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

        self.service_account_file = (
            service_account_file or
            self._get_value(
                service_account_file,
                config_key='service_account_file'
            )
        )
        if not self.service_account_file:
            raise AzureProviderException(
                'Service account file is required to connect to Azure.'
            )
        else:
            self.service_account_file = os.path.expanduser(
                self.service_account_file
            )

        self.ssh_private_key = (
            ssh_private_key or
            self._get_value(ssh_private_key, config_key='ssh_private_key')
        )
        if not self.ssh_private_key:
            raise AzureProviderException(
                'SSH private key file is required to connect to instance.'
            )
        else:
            self.ssh_private_key = os.path.expanduser(
                self.ssh_private_key
            )

        self.subscription_id = (
            subscription_id or
            self._get_value(subscription_id, config_key='subscription_id')
        )
        if not self.subscription_id:
            raise AzureProviderException(
                'Subscription ID is required to connect to instance.'
            )

        self.ssh_user = ssh_user or AZURE_DEFAULT_USER
        self.ssh_public_key = self._get_ssh_public_key()

        self._get_service_account_info()
        self.credentials = self._get_credentials()

        self.compute = self._get_compute_management()
        self.network = self._get_network_management()
        self.resource = self._get_resource_management()

        if self.running_instance_id:
            self._set_resource_names()

    def _create_network_interface(self):
        """
        Create a new vnet, subnet, public ip and network interface.

        The instance requires an IP to be accessible via SSH for testing.
        """
        try:
            vnet_operation = self.network.virtual_networks.create_or_update(
                self.running_instance_id,
                self.vnet_name,
                {
                    'location': self.region,
                    'address_space': {
                        'address_prefixes': ['10.0.0.0/27']
                    }
                }
            )
        except Exception as error:
            raise AzureProviderException(
                'Unable to create vnet: {0}.'.format(error.message)
            )

        vnet_operation.wait()

        try:
            subnet_operation = self.network.subnets.create_or_update(
                self.running_instance_id,
                self.vnet_name,
                self.subnet_name,
                {'address_prefix': '10.0.0.0/29'}
            )
        except Exception as error:
            raise AzureProviderException(
                'Unable to create subnet: {0}.'.format(error.message)
            )

        subnet_info = subnet_operation.result()

        try:
            public_ip_operation = \
                self.network.public_ip_addresses.create_or_update(
                    self.running_instance_id,
                    self.public_ip_name,
                    {
                        'location': self.region,
                        'public_ip_allocation_method': 'Dynamic'
                    }
                )
        except Exception as error:
            raise AzureProviderException(
                'Unable to create public IP: {0}.'.format(error.message)
            )

        public_ip = public_ip_operation.result()

        try:
            nic_operation = self.network.network_interfaces.create_or_update(
                self.running_instance_id,
                self.nic_name,
                {
                    'location': self.region,
                    'ip_configurations': [{
                        'name': self.ip_config_name,
                        'private_ip_allocation_method': 'Dynamic',
                        'subnet': {
                            'id': subnet_info.id
                        },
                        'public_ip_address': {
                            'id': public_ip.id
                        },
                    }]
                }
            )
        except Exception as error:
            raise AzureProviderException(
                'Unable to create network interface: {0}.'.format(
                    error.message
                )
            )

        return nic_operation.result()

    def _create_resource_group(self):
        """Create resource group if it does not exist."""
        try:
            self.resource.resource_groups.create_or_update(
                self.running_instance_id, {'location': self.region}
            )
        except Exception as error:
            raise AzureProviderException(
                'Unable to create resource group: {0}.'.format(error.message)
            )

    def _create_vm(self, vm_parameters):
        """
        Attempt to create or update VM instance based on vm_parameters config.
        """
        try:
            vm_operation = self.compute.virtual_machines.create_or_update(
                self.running_instance_id, self.running_instance_id,
                vm_parameters
            )
        except Exception as error:
            raise AzureProviderException(
                'An exception occurred creating virtual machine: {0}'.format(
                    error.message
                )
            )

        vm_operation.wait()

    def _create_vm_parameters(self, interface):
        """
        Create the VM parameters dictionary.

        Requires an existing network interface object.
        """
        # Split image ID into it's components.
        self._process_image_id()

        return {
            'location': self.region,
            'os_profile': {
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
            },
            'hardware_profile': {
                'vm_size': self.instance_type or AZURE_DEFAULT_TYPE
            },
            'storage_profile': {
                'image_reference': {
                    'publisher': self.image_publisher,
                    'offer': self.image_offer,
                    'sku': self.image_sku,
                    'version': self.image_version
                },
            },
            'network_profile': {
                'network_interfaces': [{
                    'id': interface.id,
                    'primary': True
                }]
            }
        }

    def _get_compute_management(self):
        """Return instance of compute management class."""
        return ComputeManagementClient(self.credentials, self.subscription_id)

    def _get_credentials(self):
        """Return instance of service principal credentials."""
        return ServicePrincipalCredentials(
            client_id=self.client_id,
            secret=self.client_secret,
            tenant=self.tenant_id
        )

    def _get_network_management(self):
        """Return instance of network management class."""
        return NetworkManagementClient(self.credentials, self.subscription_id)

    def _get_resource_management(self):
        """Return instance of resource management class."""
        return ResourceManagementClient(self.credentials, self.subscription_id)

    def _get_service_account_info(self):
        """Retrieve json dict from service account file."""
        try:
            with open(self.service_account_file, 'r') as f:
                info = json.load(f)
        except Exception as error:
            raise AzureProviderException(
                'Exception processing service account file: {0}.'.format(error)
            )

        try:
            self.tenant_id = info['tenant']
            self.client_id = info['appId']
            self.client_secret = info['password']
        except KeyError as error:
            raise AzureProviderException(
                'Invalid service account file, missing key: {0}.'.format(error)
            )

    def _get_ssh_public_key(self):
        """Generate SSH public key from private key."""
        key = ipa_utils.generate_public_ssh_key(self.ssh_private_key)
        return key.decode()

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
            raise AzureProviderException(
                'Unable to retrieve instance: {0}'.format(error.message)
            )

        return instance

    def _get_instance_state(self):
        """Retrieve state of instance."""
        instance = self._get_instance()
        statuses = instance.instance_view.statuses

        for status in statuses:
            if status.code.startswith('PowerState'):
                return status.display_status

    def _is_instance_running(self):
        """
        Return True if instance is in running state.
        """
        return self._get_instance_state() == 'VM running'

    def _launch_instance(self):
        """Create new test instance in a resource group with the same name."""
        self.running_instance_id = ipa_utils.generate_instance_name(
            'azure-ipa-test'
        )
        self._set_resource_names(new_instance=True)

        try:
            # Try block acts as a transaction. If an exception occurrs
            # attempt to cleanup the resource group and all resources.

            # Create resourece group with same name as instance.
            self._create_resource_group()

            # Setup network, subnet and interface in resource group.
            interface = self._create_network_interface()

            # Get dictionary of VM parameters.
            vm_parameters = self._create_vm_parameters(interface)
            self._create_vm(vm_parameters)
        except Exception:
            try:
                self._terminate_instance()
            except Exception:
                pass
            raise
        else:
            # Ensure VM is in the running state.
            self._wait_on_instance('VM running')

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
            raise AzureProviderException(
                'Image ID is invalid. Format must match '
                '{Publisher}:{Offer}:{Sku}:{Version}.'
            )

    def _set_image_id(self):
        """If an existing instance is used get image id from deployment."""
        instance = self._get_instance()
        image_info = instance.storage_profile.image_reference

        self.image_id = ':'.join([
            image_info.publisher, image_info.offer,
            image_info.sku, image_info.version
        ])

    def _set_instance_ip(self):
        """
        Get the public IP address based on instance ID.
        """
        try:
            public_ip = self.network.public_ip_addresses.get(
                self.running_instance_id, self.public_ip_name
            )
        except Exception as error:
            raise AzureProviderException(
                'Unable to retrieve instance public IP: {0}.'.format(
                    error.message
                )
            )

        self.instance_ip = public_ip.ip_address

    def _set_resource_names(self, new_instance=False):
        """
        Generate names for resources based on the running_instance_id.

        If a new instance is created the new_instance flag will be true.
        Otherwise for an existing instance only the public_ip_name is needed.
        """
        if new_instance:
            self.ip_config_name = ''.join([
                self.running_instance_id, '-ip-config'
            ])
            self.nic_name = ''.join([self.running_instance_id, '-nic'])
            self.subnet_name = ''.join([self.running_instance_id, '-subnet'])
            self.vnet_name = ''.join([self.running_instance_id, '-vnet'])

        self.public_ip_name = ''.join([self.running_instance_id, '-public-ip'])

    def _start_instance(self):
        """Start the instance."""
        try:
            start_operation = self.compute.virtual_machines.start(
                self.running_instance_id, self.running_instance_id
            )
        except Exception as error:
            raise AzureProviderException(
                'Unable to start instance: {0}.'.format(error.message)
            )

        start_operation.wait()

    def _stop_instance(self):
        """Stop the instance."""
        try:
            stop_operation = self.compute.virtual_machines.power_off(
                self.running_instance_id, self.running_instance_id
            )
        except Exception as error:
            raise AzureProviderException(
                'Unable to stop instance: {0}.'.format(error.message)
            )

        stop_operation.wait()

    def _terminate_instance(self):
        """Terminate the resource group and instance."""
        try:
            self.resource.resource_groups.delete(self.running_instance_id)
        except Exception as error:
            raise AzureProviderException(
                'Unable to terminate resource group: {0}.'.format(
                    error.message
                )
            )
