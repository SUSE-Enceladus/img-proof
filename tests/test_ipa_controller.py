#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""img_proof controller unit tests."""

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

from pytest import raises
from unittest.mock import patch

from img_proof.ipa_controller import collect_tests
from img_proof.ipa_controller import test_image as controller_test_image
from img_proof.ipa_exceptions import IpaControllerException
from img_proof.ipa_cloud import IpaCloud
from img_proof.ipa_gce import GCECloud


@patch('img_proof.ipa_controller.os')
def test_collect_tests_no_dirs(mock_os):
    """Test collect tests default directories do not exist."""
    mock_os.path.exists.return_value = False

    with raises(IpaControllerException):
        collect_tests(verbose=True)


@patch.object(IpaCloud, 'test_image')
def test_controller_azure_image(mock_test_image):
    mock_test_image.return_value = (0, {'results': 'data'})

    status, results = controller_test_image(
        cloud_name='azure',
        config='tests/data/config',
        distro='sles',
        image_id='another:fake:image:id',
        no_default_test_dirs=True,
        running_instance_id='fakeinstance',
        ssh_private_key_file='tests/data/ida_test',
        test_dirs='tests/data/tests',
        tests=['test_image'],
        service_account_file='tests/azure/test-sa.json'
    )

    assert status == 0


@patch.object(IpaCloud, 'test_image')
def test_controller_ec2_image(mock_test_image):
    mock_test_image.return_value = (0, {'results': 'data'})

    status, results = controller_test_image(
        cloud_name='ec2',
        config='tests/data/config',
        cloud_config='tests/ec2/.ec2utils.conf',
        distro='sles',
        image_id='another:fake:image:id',
        no_default_test_dirs=True,
        ssh_private_key_file='tests/data/ida_test',
        ssh_key_name='test-key',
        account='awstest'
    )

    assert status == 0


@patch.object(IpaCloud, 'test_image')
@patch.object(GCECloud, '_get_driver')
@patch.object(GCECloud, '_get_credentials')
@patch.object(GCECloud, '_validate_region')
def test_controller_gce_image(
    mock_validate_region,
    mock_get_creds,
    mock_get_driver,
    mock_test_image
):
    mock_test_image.return_value = (0, {'results': 'data'})

    status, results = controller_test_image(
        cloud_name='gce',
        config='tests/data/config',
        distro='sles',
        image_id='another:fake:image:id',
        no_default_test_dirs=True,
        ssh_private_key_file='tests/data/ida_test',
        service_account_file='tests/gce/service-account.json',
        region='us-west1-a',
        architecture='arm64'
    )

    assert status == 0


@patch.object(IpaCloud, 'test_image')
def test_controller_ssh_image(mock_test_image):
    mock_test_image.return_value = (0, {'results': 'data'})

    status, results = controller_test_image(
        cloud_name='ssh',
        config='tests/data/config',
        distro='sles',
        ip_address='another:fake:image:id',
        no_default_test_dirs=True,
        ssh_private_key_file='tests/data/ida_test',
        ssh_user='root'
    )

    assert status == 0


@patch.object(IpaCloud, 'test_image')
@patch('img_proof.ipa_oci.oci.core')
def test_controller_oci_image(mock_oci, mock_test_image):
    mock_test_image.return_value = (0, {'results': 'data'})

    status, results = controller_test_image(
        cloud_name='oci',
        config='tests/data/config',
        cloud_config='tests/oci/config',
        distro='sles',
        image_id='another:fake:image:id',
        ip_address='another:fake:image:id',
        no_default_test_dirs=True,
        ssh_private_key_file='tests/data/ida_test',
        test_dirs='tests/data/tests',
        tests=['test_image'],
        oci_user_id=(
            'ocid1.user.oc1..'
            'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
            'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
        ),
        signing_key_fingerprint=(
            '00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00'
        ),
        signing_key_file='tests/oci/api_key.pem',
        tenancy=(
            'ocid1.tenancy.oc1..'
            'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
            'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
        ),
        availability_domain='Omic:PHX-AD-1',
        compartment_id=(
            'ocid1.compartment.oc1..'
            'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
            'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
        )
    )

    assert status == 0


@patch.object(IpaCloud, 'test_image')
def test_controller_aliyun_image(mock_test_image):
    mock_test_image.return_value = (0, {'results': 'data'})

    status, results = controller_test_image(
        cloud_name='aliyun',
        config='tests/data/config',
        distro='sles',
        image_id='another:fake:image:id',
        no_default_test_dirs=True,
        ssh_private_key_file='tests/data/ida_test',
        ssh_key_name='test-key',
        access_key='1234567890',
        access_secret='0987654321',
    )

    assert status == 0
