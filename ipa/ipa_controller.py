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

import importlib
import json
import pytest
import shlex

from ipa.collect_items import CollectItemsPlugin
from ipa.ipa_constants import SUPPORTED_PROVIDERS, TEST_PATHS
from ipa.ipa_exceptions import IpaControllerException
from ipa.ipa_utils import get_test_files


def test_image(provider_name,
               access_key_id=None,
               account=None,
               cleanup=None,
               config=None,
               desc=None,
               distro=None,
               early_exit=None,
               history_log=None,
               image_id=None,
               instance_type=None,
               log_level=None,
               provider_config=None,
               region=None,
               results_dir=None,
               running_instance_id=None,
               secret_access_key=None,
               service_account_file=None,
               ssh_key_name=None,
               ssh_private_key=None,
               ssh_user=None,
               storage_container=None,
               tests=None):
    """Creates a cloud provider instance and initiates testing."""
    if provider_name in SUPPORTED_PROVIDERS:
        provider_module = importlib.import_module(
            'ipa.ipa_%s' % provider_name.lower()
        )
        provider_class = '%sProvider' % provider_name

        provider = getattr(provider_module, provider_class)(
            access_key_id=access_key_id,
            account_name=account,
            cleanup=cleanup,
            config=config,
            desc=desc,
            distro_name=distro,
            early_exit=early_exit,
            history_log=history_log,
            image_id=image_id,
            instance_type=instance_type,
            log_level=log_level,
            provider_config=provider_config,
            region=region,
            results_dir=results_dir,
            running_instance_id=running_instance_id,
            secret_access_key=secret_access_key,
            service_account_file=service_account_file,
            ssh_key_name=ssh_key_name,
            ssh_private_key=ssh_private_key,
            ssh_user=ssh_user,
            storage_container=storage_container,
            test_files=tests
        )
    else:
        raise IpaControllerException(
            'Provider: %s unavailable.' % provider_name
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
