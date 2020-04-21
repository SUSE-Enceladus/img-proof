# -*- coding: utf-8 -*-

"""Controller class for img_proof endpoints."""

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
import pytest
import shlex

from img_proof.collect_items import CollectItemsPlugin
from img_proof.ipa_azure import AzureCloud
from img_proof.ipa_constants import TEST_PATHS
from img_proof.ipa_ec2 import EC2Cloud
from img_proof.ipa_exceptions import IpaControllerException
from img_proof.ipa_gce import GCECloud
from img_proof.ipa_ssh import SSHCloud
from img_proof.ipa_oci import OCICloud
from img_proof.ipa_utils import get_test_files


def test_image(
    cloud_name,
    accelerated_networking=None,
    access_key_id=None,
    account=None,
    cleanup=None,
    config=None,
    description=None,
    distro=None,
    early_exit=None,
    history_log=None,
    image_id=None,
    image_project=None,
    inject=None,
    instance_type=None,
    ip_address=None,
    log_level=None,
    no_default_test_dirs=None,
    cloud_config=None,
    region=None,
    results_dir=None,
    running_instance_id=None,
    secret_access_key=None,
    security_group_id=None,
    service_account_file=None,
    ssh_key_name=None,
    ssh_private_key_file=None,
    ssh_user=None,
    subnet_id=None,
    test_dirs=None,
    tests=None,
    timeout=None,
    vnet_name=None,
    vnet_resource_group=None,
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
    """Creates a cloud framework instance and initiates testing."""
    kwargs = {
        'cleanup': cleanup,
        'config': config,
        'description': description,
        'distro_name': distro,
        'early_exit': early_exit,
        'history_log': history_log,
        'image_id': image_id,
        'inject': inject,
        'instance_type': instance_type,
        'log_level': log_level,
        'no_default_test_dirs': no_default_test_dirs,
        'cloud_config': cloud_config,
        'region': region,
        'results_dir': results_dir,
        'running_instance_id': running_instance_id,
        'ssh_private_key_file': ssh_private_key_file,
        'ssh_user': ssh_user,
        'subnet_id': subnet_id,
        'test_dirs': test_dirs,
        'test_files': tests,
        'timeout': timeout,
        'collect_vm_info': collect_vm_info,
        'enable_secure_boot': enable_secure_boot,
        'enable_uefi': enable_uefi
    }

    cloud_name = cloud_name.lower()
    if cloud_name == 'azure':
        cloud = AzureCloud(
            accelerated_networking=accelerated_networking,
            service_account_file=service_account_file,
            vnet_name=vnet_name,
            vnet_resource_group=vnet_resource_group,
            **kwargs
        )
    elif cloud_name == 'ec2':
        cloud = EC2Cloud(
            access_key_id=access_key_id,
            account_name=account,
            secret_access_key=secret_access_key,
            security_group_id=security_group_id,
            ssh_key_name=ssh_key_name,
            **kwargs
        )
    elif cloud_name == 'gce':
        cloud = GCECloud(
            service_account_file=service_account_file,
            image_project=image_project,
            **kwargs
        )
    elif cloud_name == 'ssh':
        cloud = SSHCloud(
            ip_address=ip_address,
            **kwargs
        )
    elif cloud_name == 'oci':
        cloud = OCICloud(
            compartment_id=compartment_id,
            availability_domain=availability_domain,
            signing_key_fingerprint=signing_key_fingerprint,
            signing_key_file=signing_key_file,
            tenancy=tenancy,
            oci_user_id=oci_user_id,
            **kwargs
        )
    else:
        raise IpaControllerException(
            'Cloud framework: %s unavailable.' % cloud_name
        )

    return cloud.test_image()


def collect_results(results_file):
    """Return the result (pass/fail) for json file."""
    with open(results_file, 'r') as results:
        data = json.load(results)
    return data


def collect_tests(test_dirs=TEST_PATHS, verbose=False):
    """Return a list of test files and/or tests cases."""
    if test_dirs:
        test_dirs = [
            test_dir for test_dir in test_dirs if os.path.exists(test_dir)
        ]

    if not test_dirs:
        raise IpaControllerException(
            'No test directories found.'
        )

    if verbose:
        plugin = CollectItemsPlugin()
        args = '--collect-only -p no:terminal {}'.format(
            ' '.join(test_dirs)
        )
        cmds = shlex.split(args)
        pytest.main(cmds, plugins=[plugin])

        return plugin.collected.values()
    else:
        tests, descriptions = get_test_files(test_dirs)
        all_tests = list(tests.keys()) + list(descriptions.keys())
        return all_tests
