# -*- coding: utf-8 -*-

"""Ipa exceptions module."""

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


class IpaException(Exception):
    """Generic exception for the ipa package."""


class IpaProviderException(IpaException):
    """Generic exception for the ipa provider."""


class AzureProviderException(IpaProviderException):
    """Generic Azure exception."""


class EC2ProviderException(IpaProviderException):
    """Generic EC2 exception."""


class GCEProviderException(IpaProviderException):
    """Generic GCE exception."""


class IpaControllerException(IpaException):
    """Generic exception for ipa controller module."""


class IpaDistroException(IpaException):
    """Generic Exception for distro modules."""


class IpaImageNotFoundException(IpaException):
    """Exception for image not found on cloud provider."""


class IpaListTestsException(IpaException):
    """List subcommand exception."""


class IpaResultsException(IpaException):
    """Results subcommand exception."""


class IpaSLESException(IpaDistroException):
    """Generic Exception for distro modules."""


class IpaTestException(IpaException):
    """Test subcommand exception."""


class IpaUtilsException(IpaException):
    """Generic exception for ipa utility methods."""


class IpaSSHException(IpaUtilsException):
    """Generic exception for ipa SSH methods."""


class LibcloudProviderException(IpaProviderException):
    """Generic libcloud exception."""
