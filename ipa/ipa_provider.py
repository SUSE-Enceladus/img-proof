# -*- coding: utf-8 -*-
#
# Copyright (c) 2017 SUSE LLC
#
# This file is part of ipa.
#
# See LICENSE for license information.

import importlib

from ipa import ipa_utils
from ipa_constants import (
    NOT_IMPLEMENTED,
    SUPPORTED_DISTROS
)
from ipa_exceptions import IpaProviderException


class IpaProvider(object):
    def __init__(self,
                 distro_name,
                 running_instance=None):
        super(IpaProvider, self).__init__()
        self.distro_name = distro_name
        self.running_instance = running_instance

    def _config(self):
        """Setup configuration."""

    def _create_ssh_config(self):
        """Create temporary ssh config file."""

    def _remove_ssh_config(self):
        """Remove temporary ssh config file."""

    def _get_instance(self):
        raise NotImplementedError(NOT_IMPLEMENTED)

    def _launch_instance(self):
        raise NotImplementedError(NOT_IMPLEMENTED)

    def _run_tests(self):
        """Runs the test suite on the image."""

    def _set_distro(self):
        """Determine distro for image and create instance of class."""
        if self.distro_name not in SUPPORTED_DISTROS:
            raise IpaProviderException(
                'Distribution: %s, not supported.' % self.distro_name
            )

        distro_module = importlib.import_module(
            'ipa.ipa_%s' % self.distro_name.lower()
        )
        self.distro = getattr(distro_module, self.distro_name)()

    def _set_instance_ip(self):
        raise NotImplementedError(NOT_IMPLEMENTED)

    def _start_instance(self):
        raise NotImplementedError(NOT_IMPLEMENTED)

    def _start_instance_if_stopped(self):
        raise NotImplementedError(NOT_IMPLEMENTED)

    def _stop_instance(self):
        raise NotImplementedError(NOT_IMPLEMENTED)

    def _terminate_instance(self):
        raise NotImplementedError(NOT_IMPLEMENTED)

    def hard_reboot_instance(self):
        """Stop then start the instance."""
        self.stop_instance()
        self.start_instance()
        self._set_instance_ip()
        ipa_utils.clear_cache()

    def test_image(self):
        """The entry point for testing an image.

        Steps:
        - Creates new or initiates existing instance
        - Optionally tests hard reboot
        - Runs test suite on instance
        - Optionally tests soft reboot
        - Collects and returns results in json format
        """
        if self.running_instance:
            # Use existing instance
            self._start_instance_if_stopped()
        else:
            # Launch new instance
            self._launch_instance()
        self._set_instance_ip()

        client = ipa_utils.get_ssh_client(
            self.instance_ip,
            self.ssh_private_key,
            self.ssh_user
        )

        self._set_distro()
