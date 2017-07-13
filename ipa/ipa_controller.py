# -*- coding: utf-8 -*-

"""Controller class for ipa endpoints."""

# Copyright (c) 2017 SUSE LLC
#
# This file is part of ipa.
#
# See LICENSE for license information.

import importlib
import json

from ipa.ipa_constants import SUPPORTED_PROVIDERS
from ipa.ipa_exceptions import IpaControllerException


def test_image(provider_name,
               access_key_id=None,
               account=None,
               cleanup=None,
               config=None,
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


def list_tests():
    """Return a list of test files and/or tests."""


def collect_results(results_file):
    """Return the result (pass/fail) for json file."""
    with open(results_file, 'r') as results:
        data = json.load(results)
    return data
