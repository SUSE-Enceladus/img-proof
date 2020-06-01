#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""img_proof oci provider unit tests."""

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

import pytest

from img_proof.ipa_oci import OCICloud
from img_proof.ipa_exceptions import OCICloudException

from unittest.mock import MagicMock, patch


class TestOCIProvider(object):
    """Test OCI provider class."""

    def setup_method(self, method):
        """Set up kwargs dict."""
        self.kwargs = {
            'config': 'tests/data/config',
            'distro_name': 'SLES',
            'image_id': 'fakeimage',
            'no_default_test_dirs': True,
            'cloud_config': 'tests/oci/config',
            'test_files': ['test_image'],
            'oci_user_id':
                'ocid1.user.oc1..'
                'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
            'signing_key_fingerprint':
                '00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00',
            'signing_key_file': 'tests/oci/api_key.pem',
            'tenancy':
                'ocid1.tenancy.oc1..'
                'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
        }

    def test_oci_exception_required_args(self):
        """Test an exception is raised if required args missing."""
        # Test missing availability domain
        with pytest.raises(OCICloudException):
            OCICloud(**self.kwargs)

        self.kwargs['availability_domain'] = 'Omic:PHX-AD-1'

        # Test missing compartment id
        with pytest.raises(OCICloudException):
            OCICloud(**self.kwargs)

        self.kwargs['compartment_id'] = (
            'ocid1.compartment.oc1..'
            'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
        )

        # Test missing ssh private key file
        with pytest.raises(OCICloudException):
            OCICloud(**self.kwargs)

    @patch('img_proof.ipa_oci.oci')
    def test_oci_init(self, mock_oci):
        """Test oci init method and config setup is successful."""
        client = MagicMock()

        mock_oci.core.ComputeClient.return_value = client
        mock_oci.core.ComputeClientCompositeOperations.return_value = client
        mock_oci.core.VirtualNetworkClient.return_value = client
        mock_oci.core.VirtualNetworkClientCompsiteOperations.return_value = client  # noqa

        self.kwargs['availability_domain'] = 'Omic:PHX-AD-1'
        self.kwargs['compartment_id'] = (
            'ocid1.compartment.oc1..'
            'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
        )
        self.kwargs['ssh_private_key_file'] = 'tests/oci/api_key.pem'

        OCICloud(**self.kwargs)

    @patch.object(OCICloud, '__init__')
    def test_oci_create_internet_gateway(self, mock_init):
        """Test oci create internet gateway method."""
        mock_init.return_value = None

        client = MagicMock()
        vcn = MagicMock()
        route_table = MagicMock()

        vcn.id = (
            'ocid1.vcn.oc1..'
            'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
        )
        vcn.default_route_table_id = (
            'ocid1.routeTable.oc1..'
            'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
        )

        gateway = MagicMock()
        gateway.id = (
            'ocid1.gateway.oc1..'
            'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
        )

        gateway_response = MagicMock()
        gateway_response.data = gateway
        client.create_internet_gateway_and_wait_for_state.return_value = gateway_response  # noqa

        route_table_response = MagicMock()
        route_table_response.data = route_table
        route_table.route_rules = []
        client.get_route_table.return_value = route_table_response

        update_table_response = MagicMock()
        update_table_response.data = []
        client.update_route_table_and_wait_for_state.return_value = update_table_response  # noqa

        cloud = OCICloud(**self.kwargs)
        cloud.vnet_composite_client = client
        cloud.vnet_client = client

        compartment_id = (
            'ocid1.compartment.oc1..'
            'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
        )
        cloud._create_internet_gateway(compartment_id, vcn, 'test-name')

    @patch.object(OCICloud, '__init__')
    def test_oci_delete_internet_gateway(self, mock_init):
        """Test oci delete internet gateway method."""
        mock_init.return_value = None

        client = MagicMock()

        gateway_id = (
            'ocid1.gateway.oc1..'
            'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
        )

        cloud = OCICloud(**self.kwargs)
        cloud.vnet_composite_client = client

        cloud._delete_internet_gateway(gateway_id)

    @patch('img_proof.ipa_oci.oci')
    @patch.object(OCICloud, '__init__')
    def test_oci_get_internet_gateway_by_name(self, mock_init, mock_oci):
        """Test oci get internet gateway by name method."""
        mock_init.return_value = None

        gateway = MagicMock()
        gateway.display_name = 'test-gw2'
        client = MagicMock()
        response = MagicMock()
        response.data = [gateway]

        mock_oci.pagination.list_call_get_all_results.return_value = response

        vcn_id = (
            'ocid1.vcn.oc1..'
            'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
        )

        cloud = OCICloud(**self.kwargs)
        cloud.vnet_client = client
        cloud.compartment_id = (
            'ocid1.compartment.oc1..'
            'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
        )

        result = cloud._get_gateway_in_vcn_by_name(vcn_id, 'test-gw2')
        assert result == gateway

    @patch.object(OCICloud, '__init__')
    def test_oci_create_vcn(self, mock_init):
        """Test oci create vcn method."""
        mock_init.return_value = None

        client = MagicMock()
        vcn = MagicMock()
        response = MagicMock()
        response.data = vcn

        client.create_vcn_and_wait_for_state.return_value = response

        cloud = OCICloud(**self.kwargs)
        cloud.compartment_id = (
            'ocid1.compartment.oc1..'
            'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
        )
        cloud.vnet_composite_client = client

        result = cloud._create_vcn('vcn-123')
        assert result == vcn

    @patch.object(OCICloud, '__init__')
    def test_oci_get_vcn(self, mock_init):
        """Test oci get vcn method."""
        mock_init.return_value = None

        client = MagicMock()
        vcn = MagicMock()
        response = MagicMock()
        response.data = vcn

        client.get_vcn.return_value = response

        cloud = OCICloud(**self.kwargs)
        cloud.vnet_client = client

        vcn_id = (
            'ocid1.vcn.oc1..'
            'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
        )

        result = cloud._get_vcn(vcn_id)
        assert result == vcn

    @patch('img_proof.ipa_oci.oci')
    @patch.object(OCICloud, '__init__')
    def test_oci_get_vcn_by_name(self, mock_init, mock_oci):
        """Test oci get vcn by name method."""
        mock_init.return_value = None

        client = MagicMock()
        vcn = MagicMock()
        vcn.display_name = 'vcn-123'
        response = MagicMock()
        response.data = [vcn]

        mock_oci.pagination.list_call_get_all_results.return_value = response

        cloud = OCICloud(**self.kwargs)
        cloud.compartment_id = (
            'ocid1.compartment.oc1..'
            'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
        )
        cloud.vnet_client = client

        result = cloud._get_vcn_by_name('vcn-123')
        assert result == vcn

    @patch.object(OCICloud, '__init__')
    def test_oci_delete_vcn(self, mock_init):
        """Test oci delete vcn method."""
        mock_init.return_value = None

        client = MagicMock()

        cloud = OCICloud(**self.kwargs)
        cloud.vnet_composite_client = client

        vcn_id = (
            'ocid1.vcn.oc1..'
            'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
        )

        cloud._delete_vcn(vcn_id)

    @patch.object(OCICloud, '__init__')
    def test_oci_create_subnet(self, mock_init):
        """Test oci create subnet method."""
        mock_init.return_value = None

        client = MagicMock()
        subnet = MagicMock()
        response = MagicMock()
        vcn = MagicMock()
        vcn.id = (
            'ocid1.vcn.oc1..'
            'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
        )
        response.data = subnet

        client.create_subnet_and_wait_for_state.return_value = response

        compartment_id = (
            'ocid1.compartment.oc1..'
            'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
        )

        cloud = OCICloud(**self.kwargs)
        cloud.vnet_composite_client = client

        result = cloud._create_subnet(
            compartment_id,
            'Omic:PHX-AD-1',
            vcn,
            'subnet-123'
        )
        assert result == subnet

    @patch.object(OCICloud, '__init__')
    def test_oci_get_subnet(self, mock_init):
        """Test oci get subnet method."""
        mock_init.return_value = None

        client = MagicMock()
        subnet = MagicMock()
        response = MagicMock()
        response.data = subnet

        client.get_subnet.return_value = response

        cloud = OCICloud(**self.kwargs)
        cloud.vnet_client = client

        subnet_id = (
            'ocid1.subnet.oc1..'
            'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
        )

        result = cloud._get_subnet(subnet_id)
        assert result == subnet

    @patch('img_proof.ipa_oci.oci')
    @patch.object(OCICloud, '__init__')
    def test_oci_get_subnet_by_name(self, mock_init, mock_oci):
        """Test oci get subnet by name method."""
        mock_init.return_value = None

        client = MagicMock()
        subnet = MagicMock()
        subnet.display_name = 'subnet-123'
        response = MagicMock()
        response.data = [subnet]

        mock_oci.pagination.list_call_get_all_results.return_value = response

        cloud = OCICloud(**self.kwargs)
        cloud.compartment_id = (
            'ocid1.compartment.oc1..'
            'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
        )
        cloud.vnet_client = client

        vcn_id = (
            'ocid1.vcn.oc1..'
            'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
        )

        result = cloud._get_subnet_by_name('subnet-123', vcn_id)
        assert result == subnet

    @patch.object(OCICloud, '__init__')
    def test_oci_delete_subnet(self, mock_init):
        """Test oci delete subnet method."""
        mock_init.return_value = None

        client = MagicMock()

        cloud = OCICloud(**self.kwargs)
        cloud.vnet_composite_client = client

        subnet_id = (
            'ocid1.subnet.oc1..'
            'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
        )

        cloud._delete_subnet(subnet_id)

    @patch.object(OCICloud, '__init__')
    def test_oci_clear_route_rules(self, mock_init):
        """Test oci clear route rules method."""
        mock_init.return_value = None

        client = MagicMock()
        vcn = MagicMock()

        cloud = OCICloud(**self.kwargs)
        cloud.vnet_composite_client = client

        vcn.default_route_table_id = (
            'ocid1.routeTable.oc1..'
            'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
        )

        cloud._clear_route_rules(vcn)

    @patch.object(OCICloud, '__init__')
    def test_oci_is_instance_running(self, mock_init):
        """Test oci is instance running method."""
        mock_init.return_value = None

        client = MagicMock()
        instance = MagicMock()
        instance.lifecycle_state = 'RUNNING'
        response = MagicMock()
        response.data = instance
        client.get_instance.return_value = response

        cloud = OCICloud(**self.kwargs)
        cloud.running_instance_id = 'instance-123'
        cloud.compute_client = client

        result = cloud._is_instance_running()
        assert result

    @patch('img_proof.ipa_oci.oci')
    @patch.object(OCICloud, '__init__')
    def test_oci_get_vnic_attachments(self, mock_init, mock_oci):
        """Test oci get vnic attachments method."""
        mock_init.return_value = None

        client = MagicMock()
        vnic = MagicMock()
        response = MagicMock()
        response.data = [vnic]

        mock_oci.pagination.list_call_get_all_results.return_value = response

        cloud = OCICloud(**self.kwargs)
        cloud.compute_client = client

        compartment_id = (
            'ocid1.compartment.oc1..'
            'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
        )
        instance_id = (
            'ocid1.instance.oc1..'
            'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
        )

        cloud._get_vnic_attachments(compartment_id, instance_id)

    @patch('img_proof.ipa_utils.get_public_ssh_key')
    @patch.object(OCICloud, '__init__')
    def test_get_ssh_public_key(self, mock_init, mock_get_public_ssh_key):
        """Test oci get ssh public key method."""
        mock_init.return_value = None
        mock_get_public_ssh_key.return_value = b'key123'

        cloud = OCICloud(**self.kwargs)
        cloud.ssh_private_key_file = 'tests/oci/api_key.pem'

        result = cloud._get_ssh_public_key()
        assert result == 'key123'

    @patch.object(OCICloud, '__init__')
    def test_get_console_log(self, mock_init):
        """Test oci get console log method."""
        mock_init.return_value = None
        response = MagicMock()
        response.data = b'Test output'
        client = MagicMock()
        client.get_console_history_content.return_value = response

        cloud = OCICloud(**self.kwargs)
        cloud.compute_client = client
        cloud.compute_composite_client = client
        cloud.running_instance_id = 'instance-123'

        log = cloud.get_console_log()
        assert log == 'Test output'

    @patch.object(OCICloud, '_wait_on_instance')
    @patch.object(OCICloud, '_terminate_instance')
    @patch.object(OCICloud, '_get_ssh_public_key')
    @patch.object(OCICloud, '_create_internet_gateway')
    @patch.object(OCICloud, '_create_subnet')
    @patch.object(OCICloud, '_create_vcn')
    @patch.object(OCICloud, '__init__')
    def test_launch_instance(
        self, mock_init, mock_create_vcn, mock_create_subnet,
        mock_create_ig, mock_get_ssh_key, mock_terminate_instance,
        mock_wait_on_instance
    ):
        """Test oci launch instance method."""
        mock_init.return_value = None

        logger = MagicMock()

        vcn = MagicMock()
        mock_create_vcn.return_value = vcn

        instance = MagicMock()
        instance.id = 'instance-123'

        response = MagicMock()
        response.data = instance

        client = MagicMock()
        client.launch_instance.return_value = response

        subnet = MagicMock()
        subnet.id = 'subnet-123'
        mock_create_subnet.return_value = subnet

        mock_get_ssh_key.return_value = 'key123'

        cloud = OCICloud(**self.kwargs)
        cloud.compute_client = client

        cloud.compartment_id = (
            'ocid1.compartment.oc1..'
            'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
        )
        cloud.availability_domain = 'Omic:PHX-AD-1'
        cloud.timeout = 600
        cloud.subnet_id = None
        cloud.instance_type = None
        cloud.image_id = 'image123'
        cloud.logger = logger

        cloud._launch_instance()

        # Test exception case
        client.launch_instance.side_effect = Exception('Broken')
        mock_terminate_instance.side_effect = Exception(
            'Cannot terminate instance'
        )

        with pytest.raises(Exception):
            cloud._launch_instance()

    @patch.object(OCICloud, '_get_instance')
    @patch.object(OCICloud, '__init__')
    def test_set_image_id(self, mock_init, mock_get_instance):
        """Test oci set image id method."""
        mock_init.return_value = None

        instance = MagicMock()
        instance.display_name = 'instance 123'
        instance.source_details.image_id = 'image123'

        mock_get_instance.return_value = instance
        cloud = OCICloud(**self.kwargs)
        cloud._set_image_id()

    @patch.object(OCICloud, '_get_vnic_attachments')
    @patch.object(OCICloud, '_get_instance')
    @patch.object(OCICloud, '__init__')
    def test_set_instance_ip(
        self, mock_init, mock_get_instance, mock_get_vnic_attachments
    ):
        """Test oci set instance ip method."""
        mock_init.return_value = None

        instance = MagicMock()
        instance.id = 'instance123'
        instance.compartment_id = (
            'ocid1.compartment.oc1..'
            'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
        )

        attachment = MagicMock()
        attachment.vnic_id = 'vnic123'

        mock_get_vnic_attachments.return_value = [attachment]

        vnic = MagicMock()
        vnic.public_ip = '0.0.0.0'
        vnic.private_ip = '10.0.0.123'

        response = MagicMock()
        response.data = vnic

        client = MagicMock()
        client.get_vnic.return_value = response

        mock_get_instance.return_value = instance

        cloud = OCICloud(**self.kwargs)
        cloud.vnet_client = client

        cloud._set_instance_ip()

    @patch.object(OCICloud, '_wait_on_instance')
    @patch.object(OCICloud, '__init__')
    def test_start_instance(self, mock_init, mock_wait_on_instance):
        """Test oci start instance method."""
        mock_init.return_value = None

        client = MagicMock()

        cloud = OCICloud(**self.kwargs)
        cloud.compute_client = client
        cloud.running_instance_id = 'instance123'
        cloud.timeout = 600

        cloud._start_instance()

    @patch.object(OCICloud, '_wait_on_instance')
    @patch.object(OCICloud, '__init__')
    def test_stop_instance(self, mock_init, mock_wait_on_instance):
        """Test oci stop instance method."""
        mock_init.return_value = None

        client = MagicMock()

        cloud = OCICloud(**self.kwargs)
        cloud.compute_client = client
        cloud.running_instance_id = 'instance123'
        cloud.timeout = 600

        cloud._stop_instance()

    @patch.object(OCICloud, '_delete_vcn')
    @patch.object(OCICloud, '_delete_internet_gateway')
    @patch.object(OCICloud, '_get_gateway_in_vcn_by_name')
    @patch.object(OCICloud, '_clear_route_rules')
    @patch.object(OCICloud, '_delete_subnet')
    @patch.object(OCICloud, '_get_subnet_by_name')
    @patch.object(OCICloud, '_get_vcn_by_name')
    @patch.object(OCICloud, '__init__')
    def test_terminate_instance(
        self, mock_init, mock_get_vcn, mock_get_subnet, mock_delete_subnet,
        mock_clear_route_rules, mock_get_gateway, mock_delete_gateway,
        mock_delete_vcn
    ):
        """Test oci terminate instance method."""
        mock_init.return_value = None

        client = MagicMock()

        vcn = MagicMock()
        vcn.id = 'vcn123'
        mock_get_vcn.return_value = vcn

        subnet = MagicMock()
        subnet.id = 'subnet123'
        mock_get_subnet.return_value = subnet

        gateway = MagicMock()
        gateway.id = 'gateway123'
        mock_get_gateway.return_value = gateway

        cloud = OCICloud(**self.kwargs)
        cloud.compute_composite_client = client
        cloud.running_instance_id = 'instance123'
        cloud.display_name = 'oci-ipa-test'
        cloud.timeout = 600

        cloud._terminate_instance()

        # No VCN
        mock_get_vcn.return_value = None
        cloud._terminate_instance()

        # Display name not created by img-proof
        cloud.display_name = 'not-ipa-test'
        cloud._terminate_instance()
