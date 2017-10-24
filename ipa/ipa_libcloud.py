# -*- coding: utf-8 -*-

"""Provider module for testing images with libcloud."""

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

from ipa.ipa_exceptions import LibcloudProviderException
from ipa.ipa_provider import IpaProvider


class LibcloudProvider(IpaProvider):
    """Provider class for testing images with libcloud."""

    def _get_image(self):
        """Retrieve NodeImage given the image id."""
        try:
            image = self.compute_driver.get_image(self.image_id)
        except Exception:
            raise LibcloudProviderException(
                'Image with ID: {image_id} not found.'.format(
                    image_id=self.image_id
                )
            )

        return image

    def _get_instance_size(self, default_type):
        """Retrieve NodeSize given the instance type."""
        instance_type = self.instance_type or default_type

        try:
            sizes = self.compute_driver.list_sizes(location=self.region)
            size = [
                size for size in sizes if size.name == instance_type
                or size.id == instance_type
            ][0]
        except IndexError:
            raise LibcloudProviderException(
                'Instance type: {instance_type} not found.'.format(
                    instance_type=instance_type
                )
            )

        return size

    def _get_instance_state(self):
        """Attempt to retrieve the state of the instance."""
        instance = self._get_instance()
        return instance.state

    def _is_instance_running(self):
        """Return True if instance is in running state."""
        return self._get_instance_state() == 'running'

    def _set_instance_ip(self):
        """Retrieve and set the instance ip address."""
        instance = self._get_instance()

        try:
            self.instance_ip = instance.public_ips[0]
        except IndexError:
            raise LibcloudProviderException(
                'IP address for instance: %s cannot be found.'
                % self.running_instance_id
            )

    def _start_instance(self):
        """Start the instance."""
        instance = self._get_instance()
        self.compute_driver.ex_start_node(instance)
        self.compute_driver.wait_until_running([instance])

    def _stop_instance(self):
        """Stop the instance."""
        instance = self._get_instance()
        self.compute_driver.ex_stop_node(instance)
        self._wait_on_instance('stopped')

    def _terminate_instance(self):
        """Terminate the instance."""
        instance = self._get_instance()
        instance.destroy()
