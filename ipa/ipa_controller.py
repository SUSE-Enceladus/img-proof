# -*- coding: utf-8 -*-

"""Controller class for ipa endpoints."""

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
import pytest
import shlex

from ipa.collect_items import CollectItemsPlugin
from ipa.ipa_azure import AzureProvider
from ipa.ipa_constants import TEST_PATHS
from ipa.ipa_ec2 import EC2Provider
from ipa.ipa_exceptions import IpaControllerException
from ipa.ipa_gce import GCEProvider
from ipa.ipa_ssh import SSHProvider
from ipa.ipa_utils import get_test_files


def test_image(provider_name,
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
               inject=None,
               instance_type=None,
               ip_address=None,
               log_level=None,
               no_default_test_dirs=None,
               provider_config=None,
               region=None,
               results_dir=None,
               running_instance_id=None,
               secret_access_key=None,
               service_account_file=None,
               ssh_key_name=None,
               ssh_private_key_file=None,
               ssh_user=None,
               subnet_id=None,
               test_dirs=None,
               tests=None,
               timeout=None,
               vnet_name=None,
               vnet_resource_group=None):
    """Creates a cloud provider instance and initiates testing."""
    provider_name = provider_name.lower()
    if provider_name == 'azure':
        provider_class = AzureProvider
    elif provider_name == 'ec2':
        provider_class = EC2Provider
    elif provider_name == 'gce':
        provider_class = GCEProvider
    elif provider_name == 'ssh':
        provider_class = SSHProvider
    else:
        raise IpaControllerException(
            'Provider: %s unavailable.' % provider_name
        )

    provider = provider_class(
        accelerated_networking=accelerated_networking,
        access_key_id=access_key_id,
        account_name=account,
        cleanup=cleanup,
        config=config,
        description=description,
        distro_name=distro,
        early_exit=early_exit,
        history_log=history_log,
        image_id=image_id,
        inject=inject,
        instance_type=instance_type,
        ip_address=ip_address,
        log_level=log_level,
        no_default_test_dirs=no_default_test_dirs,
        provider_config=provider_config,
        region=region,
        results_dir=results_dir,
        running_instance_id=running_instance_id,
        secret_access_key=secret_access_key,
        service_account_file=service_account_file,
        ssh_key_name=ssh_key_name,
        ssh_private_key_file=ssh_private_key_file,
        ssh_user=ssh_user,
        subnet_id=subnet_id,
        test_dirs=test_dirs,
        test_files=tests,
        timeout=timeout,
        vnet_name=vnet_name,
        vnet_resource_group=vnet_resource_group
    )

    return provider.test_image()


def collect_results(results_file):
    """Return the result (pass/fail) for json file."""
    with open(results_file, 'r') as results:
        data = json.load(results)
    return data


def collect_tests(test_dirs, verbose=False):
    """Return a list of test files and/or tests cases."""
    if not test_dirs:
        test_dirs = TEST_PATHS

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
