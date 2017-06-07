# -*- coding: utf-8 -*-
#
# Copyright (c) 2017 SUSE LLC
#
# This file is part of ipa.
#
# See LICENSE for license information.

from ipa.ipa_provider import IpaProvider


class EC2Provider(IpaProvider):
    def __init__(self,
                 distro_name,
                 running_instance=None,
                 ssh_private_key=None,
                 ssh_user=None):
        super(EC2Provider, self).__init__(
            distro_name,
            'EC2',
            running_instance
        )
        self.ssh_private_key = ssh_private_key
        self.ssh_user = ssh_user or 'ec2-user'

    def _config(self):
        """Setup configuration."""

    def _connect(self):
        """Connect to ec2 resource."""

    def _get_instance(self):
        """Retrieve instance matching instance_id."""

    def _get_instance_state(self):
        """Attempt to retrieve the state of the instance."""

    def _is_instance_running(self):
        """Return True if instance is in running state."""

    def _launch_instance(self):
        """Launch an instance of the given image."""

    def _set_instance_ip(self):
        """Retrieve and set the instance ip address."""

    def _start_instance(self):
        """Start the instance."""

    def _stop_instance(self):
        """Stop the instance."""

    def _terminate_instance(self):
        """Terminate the instance."""
