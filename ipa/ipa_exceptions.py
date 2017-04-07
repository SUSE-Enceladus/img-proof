# -*- coding: utf-8 -*-
#
# Copyright (c) 2017 SUSE LLC
#
# This file is part of ipa.
#
# See LICENSE for license information.


class IpaProviderException(Exception):
    """Generic exception for the ipa package."""


class AzureProviderException(IpaProviderException):
    """Generic Azure exception."""


class EC2ProviderException(IpaProviderException):
    """Generic EC2 exception."""


class GCEProviderException(IpaProviderException):
    """Generic GCE exception."""


class IpaDistroException(IpaProviderException):
    """Generic Exception for distro modules."""


class IpaImageNotFoundException(IpaProviderException):
    """Exception for image not found on cloud provider."""


class IpaListTestsException(IpaProviderException):
    """List subcommand exception."""


class IpaResultsException(IpaProviderException):
    """Results subcommand exception."""


class IpaTestException(IpaProviderException):
    """Test subcommand exception."""
