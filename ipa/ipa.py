# -*- coding: utf-8 -*-
#
# Copyright (c) 2017 SUSE LLC
#
# This file is part of ipa.
#
# See LICENSE for license information.

import ipa_utils

from ipa_constants import NOT_IMPLEMENTED


class IpaProvider(object):
    def __init__(self):
        super(IpaProvider, self).__init__()

    def _config(self):
        """Setup configuration."""

    def _create_ssh_config(self):
        """Create temporary ssh config file."""

    def _remove_ssh_config(self):
        """Remove temporary ssh config file."""

    def get_instance(self):
        raise NotImplementedError(NOT_IMPLEMENTED)

    def hard_reboot_instance(self):
        """Stop then start the instance."""
        self.stop_instance()
        self.start_instance()
        ipa_utils.clear_cache()
        print('Instance rebooted')

    def initiate_instance(self):
        raise NotImplementedError(NOT_IMPLEMENTED)

    def launch_instance(self):
        raise NotImplementedError(NOT_IMPLEMENTED)

    def start_instance(self):
        raise NotImplementedError(NOT_IMPLEMENTED)

    def stop_instance(self):
        raise NotImplementedError(NOT_IMPLEMENTED)

    def terminate_instance(self):
        raise NotImplementedError(NOT_IMPLEMENTED)

    def test_image(self):
        """The entry point for testing an image.

        This method will perform the following steps:
          - launch_instance() # If a host is passed in this is skipped
          - system_reboot()
          - system_update()
          - reboot_instance()
          - run_tests()
          - terminate_instance() # Optional depends on test results and -c flag
        """

    def run_tests(self):
        """Runs the test suite on the image."""

    def system_reboot(self):
        """Performs a system reboot."""

    def system_update(self):
        """Updates the instace based on OS type.

        E.g. for SUSE `zypper up`
        """
