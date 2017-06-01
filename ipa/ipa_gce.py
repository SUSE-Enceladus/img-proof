# -*- coding: utf-8 -*-
#
# Copyright (c) 2017 SUSE LLC
#
# This file is part of ipa.
#
# See LICENSE for license information.

from ipa import IpaProvider


class GCEProvider(IpaProvider):
    def __init__(self):
        super(GCEProvider, self).__init__()

    def _config(self):
        """Setup configuration."""

    def _connect(self):
        """Connect to gce resource."""

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
