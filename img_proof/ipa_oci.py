# -*- coding: utf-8 -*-

"""Cloud module for testing Oracle OCI images."""

# Copyright (c) 2019 SUSE LLC. All rights reserved.
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

import oci

from img_proof import ipa_utils
from img_proof.ipa_constants import (
    OCI_DEFAULT_TYPE,
    OCI_DEFAULT_USER
)
from img_proof.ipa_exceptions import OCICloudException
from img_proof.ipa_cloud import IpaCloud


class OCICloud(IpaCloud):
    """Cloud framework class for testing Oracle OCI images."""

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
        ssh_private_key_file=None,
        ssh_user=None,
        subnet_id=None,
        test_dirs=None,
        test_files=None,
        timeout=None,
        collect_vm_info=None,
        compartment_id=None,
        availability_domain=None,
        signing_key_fingerprint=None,
        signing_key_file=None,
        tenancy=None,
        oci_user_id=None,
        enable_secure_boot=None,
        enable_uefi=None
    ):
        """Initialize OCI cloud framework class."""
        super(OCICloud, self).__init__(
            'oci',
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

        self.availability_domain = (
            availability_domain or self.ipa_config['availability_domain']
        )

        if not self.availability_domain:
            raise OCICloudException(
                'Availability domain is required to connect to OCI.'
            )

        self.compartment_id = (
            compartment_id or self.ipa_config['compartment_id']
        )

        if not self.compartment_id:
            raise OCICloudException(
                'Compartment ID is required to use OCI.'
            )

        if not self.ssh_private_key_file:
            raise OCICloudException(
                'SSH private key file is required to connect to instance.'
            )

        self.ssh_user = self.ssh_user or OCI_DEFAULT_USER
        self.subnet_id = subnet_id or self.ipa_config['subnet_id']
        self.oci_user_id = oci_user_id or self.ipa_config['oci_user_id']
        self.tenancy = tenancy or self.ipa_config['tenancy']
        self.signing_key_fingerprint = (
            signing_key_fingerprint
            or self.ipa_config['signing_key_fingerprint']
        )
        self.signing_key_file = (
            signing_key_file or self.ipa_config['signing_key_file']
        )

        config = self._get_config()
        self.compute_client = oci.core.ComputeClient(config)
        self.compute_composite_client = \
            oci.core.ComputeClientCompositeOperations(
                self.compute_client
            )
        self.vnet_client = oci.core.VirtualNetworkClient(config)
        self.vnet_composite_client = \
            oci.core.VirtualNetworkClientCompositeOperations(
                self.vnet_client
            )

    def _create_internet_gateway(self, compartment_id, vcn, display_name):
        """Create gateway in VCN."""
        response = self.vnet_composite_client.create_internet_gateway_and_wait_for_state(  # noqa
            oci.core.models.CreateInternetGatewayDetails(
                display_name=display_name + '-gateway',
                compartment_id=compartment_id,
                is_enabled=True,
                vcn_id=vcn.id
            ),
            wait_for_states=[
                oci.core.models.InternetGateway.LIFECYCLE_STATE_AVAILABLE
            ]
        )
        internet_gateway = response.data

        self._add_route_rule_to_gateway(internet_gateway, vcn)

        return internet_gateway

    def _delete_internet_gateway(self, gateway_id):
        """Delete gateway matching id."""
        self.vnet_composite_client.delete_internet_gateway_and_wait_for_state(
            gateway_id,
            wait_for_states=[
                oci.core.models.InternetGateway.LIFECYCLE_STATE_TERMINATED
            ]
        )

    def _get_gateway_in_vcn_by_name(self, vcn_id, display_name):
        """
        Return gateway in VCN that matches display name.

        Return None if no gateway matches display name.
        """
        gateways = self._list_gateways_in_vcn(self.compartment_id, vcn_id)

        gateway = None
        for ig in gateways:
            if ig.display_name == display_name:
                gateway = ig
                break

        return gateway

    def _list_gateways_in_vcn(self, compartment_id, vcn_id):
        """Return a list of all gateways in VCN."""
        gateways = oci.pagination.list_call_get_all_results(
            self.vnet_client.list_internet_gateways,
            compartment_id=compartment_id,
            vcn_id=vcn_id
        ).data

        return gateways

    def _create_vcn(self, display_name, cidr_block='10.0.0.0/29'):
        """
        Create VCN in the default compartment.
        """
        response = self.vnet_composite_client.create_vcn_and_wait_for_state(
            oci.core.models.CreateVcnDetails(
                cidr_block=cidr_block,
                display_name=display_name + '-vcn',
                compartment_id=self.compartment_id
            ),
            wait_for_states=[oci.core.models.Vcn.LIFECYCLE_STATE_AVAILABLE]
        )
        vcn = response.data

        return vcn

    def _get_vcn(self, vcn_id):
        """Return VCN matching id."""
        return self.vnet_client.get_vcn(vcn_id).data

    def _get_vcn_by_name(self, vcn_name):
        """
        Return VCN that matches the display name.

        Return None if no VCNs found matching the name.
        """
        vcns = oci.pagination.list_call_get_all_results(
            self.vnet_client.list_vcns,
            compartment_id=self.compartment_id,
            display_name=vcn_name
        ).data
        return vcns[0] if vcns else None

    def _delete_vcn(self, vcn_id):
        """Delete VCN that matches id."""
        self.vnet_composite_client.delete_vcn_and_wait_for_state(
            vcn_id,
            wait_for_states=[oci.core.models.Vcn.LIFECYCLE_STATE_TERMINATED]
        )

    def _create_subnet(
        self,
        compartment_id,
        availability_domain,
        vcn,
        display_name
    ):
        """Create a new subnet in the provided VCN."""
        response = self.vnet_composite_client.create_subnet_and_wait_for_state(  # noqa
            oci.core.models.CreateSubnetDetails(
                compartment_id=compartment_id,
                availability_domain=availability_domain,
                display_name=display_name + '-subnet',
                vcn_id=vcn.id,
                cidr_block=vcn.cidr_block
            ),
            wait_for_states=[oci.core.models.Subnet.LIFECYCLE_STATE_AVAILABLE]
        )
        subnet = response.data

        return subnet

    def _get_subnet(self, subnet_id):
        """Return subnet based on id."""
        return self.vnet_client.get_subnet(subnet_id).data

    def _get_subnet_by_name(self, subnet_name, vcn_id):
        """
        Return subnet that matches the display name.

        Return None if no subnets found matching the display name.
        """
        subnets = oci.pagination.list_call_get_all_results(
            self.vnet_client.list_subnets,
            compartment_id=self.compartment_id,
            vcn_id=vcn_id,
            display_name=subnet_name
        ).data
        return subnets[0] if subnets else None

    def _delete_subnet(self, subnet_id):
        """Delete subnet given the id."""
        self.vnet_composite_client.delete_subnet_and_wait_for_state(
            subnet_id,
            wait_for_states=[oci.core.models.Subnet.LIFECYCLE_STATE_TERMINATED]
        )

    def _add_route_rule_to_gateway(self, internet_gateway, vcn):
        """Add route rule to enable SSH to instance VCN."""
        response = self.vnet_client.get_route_table(
            vcn.default_route_table_id
        )
        route_rules = response.data.route_rules

        route_rules.append(
            oci.core.models.RouteRule(
                cidr_block='0.0.0.0/0',
                network_entity_id=internet_gateway.id
            )
        )

        response = self.vnet_composite_client.update_route_table_and_wait_for_state(  # noqa
            vcn.default_route_table_id,
            oci.core.models.UpdateRouteTableDetails(route_rules=route_rules),
            wait_for_states=[
                oci.core.models.RouteTable.LIFECYCLE_STATE_AVAILABLE
            ]
        )
        route_rules = response.data

        return route_rules

    def _clear_route_rules(self, vcn):
        """Clear all route rules for the VCN."""
        self.vnet_composite_client.update_route_table_and_wait_for_state(
            vcn.default_route_table_id,
            oci.core.models.UpdateRouteTableDetails(route_rules=[]),
            wait_for_states=[
                oci.core.models.RouteTable.LIFECYCLE_STATE_AVAILABLE
            ]
        )

    def _get_config(self):
        """
        Attempt to get OCI config by file.

        If config file does not exist continue with values passed
        in to CLI and img-proof config files.
        """
        kwargs = {}
        config = {}

        if self.cloud_config:
            kwargs['file_location'] = self.cloud_config

        try:
            config = oci.config.from_file(**kwargs)
        except Exception:
            pass

        if self.oci_user_id:
            config['user'] = self.oci_user_id

        if self.signing_key_file:
            config['key_file'] = self.signing_key_file

        if self.signing_key_fingerprint:
            config['fingerprint'] = self.signing_key_fingerprint

        if self.tenancy:
            config['tenancy'] = self.tenancy

        if self.region:
            config['region'] = self.region

        return config

    def _get_instance(self):
        """Retrieve instance matching instance_id."""
        try:
            instance = self.compute_client.get_instance(
                self.running_instance_id
            ).data
        except Exception:
            raise OCICloudException(
                'Instance with ID: {instance_id} not found.'.format(
                    instance_id=self.running_instance_id
                )
            )
        return instance

    def _get_instance_state(self):
        """
        Attempt to retrieve the state of the instance.

        Raises:
            OCICloudException: If the instance cannot be found.
        """
        instance = self._get_instance()

        try:
            state = instance.lifecycle_state
        except Exception:
            raise OCICloudException(
                'Instance with id: {instance_id}, '
                'cannot be found.'.format(
                    instance_id=self.running_instance_id
                )
            )

        return state

    def _get_vnic_attachments(self, compartment_id, instance_id):
        """Return a list of vnics attached to the given instance."""
        vnic_attachments = oci.pagination.list_call_get_all_results(
            self.compute_client.list_vnic_attachments,
            compartment_id=compartment_id,
            instance_id=instance_id
        ).data

        return vnic_attachments

    def _is_instance_running(self):
        """
        Return True if instance is in running state.
        """
        return self._get_instance_state().lower() == 'running'

    def _get_ssh_public_key(self):
        """Generate SSH public key from private key."""
        key = ipa_utils.get_public_ssh_key(self.ssh_private_key_file)
        return key.decode()

    def get_console_log(self):
        """
        Return console log output if it is available.
        """
        states = [
            oci.core.models.ConsoleHistory.LIFECYCLE_STATE_SUCCEEDED
        ]

        try:
            history_details = oci.core.models.CaptureConsoleHistoryDetails(
                instance_id=self.running_instance_id
            )
            result = self.compute_composite_client.\
                capture_console_history_and_wait_for_state(
                    history_details,
                    wait_for_states=states
                ).data
            output = self.compute_client.get_console_history_content(
                result.id
            ).data
            history = output.decode()
        except Exception:
            history = ''

        return history

    def _launch_instance(self):
        """Launch an instance of the given image."""
        self.display_name = ipa_utils.generate_instance_name('oci-ipa-test')

        try:
            if not self.subnet_id:
                self.vcn = self._create_vcn(self.display_name)
                subnet = self._create_subnet(
                    self.compartment_id,
                    self.availability_domain,
                    self.vcn,
                    self.display_name
                )
                self._create_internet_gateway(
                    self.compartment_id,
                    self.vcn,
                    self.display_name
                )
                self.subnet_id = subnet.id

            instance_metadata = {
                'ssh_authorized_keys': self._get_ssh_public_key()
            }

            launch_instance_details = oci.core.models.LaunchInstanceDetails(
                display_name=self.display_name,
                compartment_id=self.compartment_id,
                availability_domain=self.availability_domain,
                shape=self.instance_type or OCI_DEFAULT_TYPE,
                metadata=instance_metadata,
                source_details=oci.core.models.InstanceSourceViaImageDetails(
                    image_id=self.image_id
                ),
                create_vnic_details=oci.core.models.CreateVnicDetails(
                    subnet_id=self.subnet_id
                )
            )

            response = self.compute_client.launch_instance(
                launch_instance_details
            )
            instance = response.data
        except Exception as error:
            try:
                self._terminate_instance()
            except Exception:
                pass

            if hasattr(error, 'message'):
                raise OCICloudException(error.message)
            else:
                raise
        else:
            self.running_instance_id = instance.id
            self.logger.debug('ID of instance: %s' % self.running_instance_id)
            self._wait_on_instance('RUNNING', self.timeout)

    def _set_image_id(self):
        """If existing instance used get image id."""
        instance = self._get_instance()
        self.display_name = instance.display_name
        self.image_id = instance.source_details.image_id

    def _set_instance_ip(self):
        """
        Retrieve instance ip and cache it.
        """
        instance = self._get_instance()
        self.instance_ip = None

        vnic_attachments = self._get_vnic_attachments(
            instance.compartment_id,
            instance.id
        )

        for attachment in vnic_attachments:
            vnic = self.vnet_client.get_vnic(
                attachment.vnic_id
            ).data

            public_address = vnic.public_ip
            private_address = vnic.private_ip

            if public_address or private_address:
                # Current nic has an IP address, set and finish
                self.instance_ip = public_address or private_address
                break

        if not self.instance_ip:
            raise OCICloudException(
                'IP address for instance cannot be found.'
            )

    def _start_instance(self):
        """Start the instance."""
        self.compute_client.instance_action(
            self.running_instance_id,
            'START'
        )
        self._wait_on_instance('RUNNING', self.timeout)

    def _stop_instance(self):
        """Stop the instance."""
        self.compute_client.instance_action(
            self.running_instance_id,
            'STOP'
        )
        self._wait_on_instance('STOPPED', self.timeout)

    def _terminate_instance(self):
        """Terminate the instance."""
        self.compute_composite_client.terminate_instance_and_wait_for_state(
            self.running_instance_id,
            wait_for_states=[
                oci.core.models.Instance.LIFECYCLE_STATE_TERMINATED
            ]
        )

        if not self.display_name.startswith('oci-ipa-test'):
            # Only cleanup artifacts created by img-proof
            return

        vcn = self._get_vcn_by_name(self.display_name + '-vcn')

        if not vcn:
            return

        subnet = self._get_subnet_by_name(
            self.display_name + '-subnet',
            vcn.id
        )

        if subnet:
            self._delete_subnet(subnet.id)

        # Route table references gateway
        self._clear_route_rules(vcn)

        gateway = self._get_gateway_in_vcn_by_name(
            vcn.id,
            self.display_name + '-gateway'
        )

        if gateway:
            self._delete_internet_gateway(gateway.id)

        self._delete_vcn(vcn.id)
