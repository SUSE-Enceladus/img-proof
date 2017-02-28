# -*- coding: utf-8 -*-
#
# Copyright (c) 2017 SUSE LLC, Sean marlow
#
# This file is part of ipa.
#
# See LICENSE for license information.

from ipa import IpaProvider


class Ec2Provider(IpaProvider):
    def __init__(self):
        super(AzureProvider, self).__init__()

    def _config(self):
        """Setup configuration."""

    def _connect(self):
        """Connect to ec2 resource."""

    def get_instance(self):
        """Retrieve instance matching instance_id."""

    def launch_instance(self):
        """Launch an instance of the given image."""

    def reboot_instance(self):
        """Framework reboot instance."""

    def start_instance(self):
        """Start the instance."""

    def stop_instance(self):
        """Stop the instance."""

    def terminate_instance(self):
        """Terminate the instance."""

