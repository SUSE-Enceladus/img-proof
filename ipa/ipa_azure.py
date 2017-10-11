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

import azurectl.logger

from azurectl.account.service import AzureAccount
from azurectl.config.parser import Config as AzurectlConfig
from azurectl.instance.cloud_service import CloudService
from azurectl.instance.virtual_machine import VirtualMachine
from azurectl.management.request_result import RequestResult

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
                 storage_container=None,
                 test_dirs=None,
                 test_files=None):
        """Initialize Azure Provider class."""
        super(AzureProvider, self).__init__('Azure',
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

        azurectl.logger.init()
        self.account_name = account_name

        if not ssh_private_key:
            raise AzureProviderException(
                'SSH private key file is required to connect to instance.'
            )
        else:
            self.ssh_private_key = ssh_private_key

        self.ssh_user = ssh_user or AZURE_DEFAULT_USER
        self.storage_container = storage_container
        self.account = self._get_account()
        self.vm = self._get_virtual_machine()

    def _create_cloud_service(self, instance_name):
        """Create cloud service if it does not exist."""
        cloud_service = self._get_cloud_service()
        request_id = cloud_service.create(
            instance_name,
            self.region
        )

        if int(request_id, 16) > 0:
            # Cloud service created
            self._wait_on_request(request_id)

        return cloud_service

    def _get_account(self):
        """Create an account object."""
        if self.provider_config:
            self.logger.debug(
                'Using Azure config file: %s' % self.provider_config
            )
        else:
            self.logger.debug('Using default Azure config file')

        config = AzurectlConfig(
            account_name=self.account_name,
            filename=self.provider_config,
            region_name=self.region,
            storage_container_name=self.storage_container
        )

        return AzureAccount(config)

    def _get_cloud_service(self):
        """Return instance of CloudService class."""
        return CloudService(self.account)

    def _get_instance_state(self):
        """Retrieve state of instance."""
        return self.vm.instance_status(self.running_instance_id)

    def _get_virtual_machine(self):
        """Return instance of VirtualMachine class."""
        return VirtualMachine(self.account)

    def _is_instance_running(self):
        """
        Return True if instance is in running state.

        Raises:
            AzureProviderException: If state is Undefined.
        """
        state = self._get_instance_state()

        if state == 'Undefined':
            raise AzureProviderException(
                'Instance with name: %s, '
                'cannot be found.' % self.running_instance_id
            )

        return state == 'ReadyRole'

    def _launch_instance(self):
        """Create new test instance in cloud service with same name."""
        instance_name = ipa_utils.generate_instance_name(
            'azure-ipa-test'
        )

        cloud_service = self._create_cloud_service(instance_name)
        fingerprint = cloud_service.add_certificate(
            instance_name,
            self.ssh_private_key
        )

        linux_configuration = self.vm.create_linux_configuration(
            instance_name=instance_name,
            fingerprint=fingerprint
        )

        ssh_endpoint = self.vm.create_network_endpoint(
            name='SSH',
            public_port=22,
            local_port=22,
            protocol='TCP'
        )

        network_configuration = self.vm.create_network_configuration(
            [ssh_endpoint]
        )

        self.vm.create_instance(
            instance_name,
            self.image_id,
            linux_configuration,
            network_config=network_configuration,
            machine_size=self.instance_type or AZURE_DEFAULT_TYPE
        )

        self.running_instance_id = instance_name
        self._wait_on_instance('ReadyRole')

    def _set_image_id(self):
        """If an existing instance is used get image id from deployment."""
        try:
            properties = self.vm.service.get_hosted_service_properties(
                service_name=self.running_instance_id,
                embed_detail=True
            )
            self.image_id = properties.deployments[0].role_list[0]\
                .os_virtual_hard_disk.source_image_name
        except IndexError:
            raise AzureProviderException(
                'Image name for instance cannot be found.'
            )

    def _set_instance_ip(self):
        """
        Get the first ip from first deployment.

        There is only one vm in current cloud service.
        """
        cloud_service = self._get_cloud_service()
        service_info = cloud_service.get_properties(self.running_instance_id)

        try:
            self.instance_ip = \
                    service_info['deployments'][0]['virtual_ips'][0]['address']
        except IndexError:
            raise AzureProviderException(
                'IP address for instance cannot be found.'
            )

    def _start_instance(self):
        """Start the instance."""
        self.vm.start_instance(
           cloud_service_name=self.running_instance_id,
           instance_name=self.running_instance_id
        )
        self._wait_on_instance('ReadyRole')

    def _stop_instance(self):
        """Stop the instance."""
        self.vm.shutdown_instance(
            cloud_service_name=self.running_instance_id,
            instance_name=self.running_instance_id,
            deallocate_resources=True
        )
        self._wait_on_instance('StoppedDeallocated')

    def _terminate_instance(self):
        """Terminate the cloud service and instance."""
        cloud_service = self._get_cloud_service()
        cloud_service.delete(self.running_instance_id, complete=True)

    def _wait_on_request(self, request_id):
        """Wait for request to complete."""
        service = self.account.get_management_service()
        request_result = RequestResult(request_id)
        request_result.wait_for_request_completion(service)
