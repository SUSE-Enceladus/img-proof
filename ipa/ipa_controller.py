"""Controller class for ipa endpoints."""
# -*- coding: utf-8 -*-
#
# Copyright (c) 2017 SUSE LLC
#
# This file is part of ipa.
#
# See LICENSE for license information.

import importlib

from ipa.ipa_constants import SUPPORTED_PROVIDERS
from ipa.ipa_exceptions import IpaControllerException


def test_image(provider_name,
               distro=None,
               running_instance=None,
               ssh_private_key=None,
               ssh_user=None):
    """Creates a cloud provider instance and initiates testing."""
    if provider_name in SUPPORTED_PROVIDERS:
        provider_module = importlib.import_module(
            'ipa.ipa_%s' % provider_name.lower()
        )
        provider_class = '%sProvider' % provider_name

        provider = getattr(provider_module, provider_class)(
            distro_name=distro,
            running_instance=running_instance,
            ssh_private_key=ssh_private_key,
            ssh_user=ssh_user,
        )
    else:
        raise IpaControllerException(
            'Provider: %s unavailable.' % provider_name
        )

    return provider.test_image()

def list_tests():
    """Returns a list of test files and/or tests."""

def collect_results():
    """Returns the result (pass/fail) or verbose results."""
