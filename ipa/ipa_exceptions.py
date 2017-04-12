# -*- coding: utf-8 -*-
#
# Copyright (c) 2017 SUSE LLC
#
# This file is part of ipa.
#
# See LICENSE for license information.


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


class IpaSUSEException(IpaDistroException):
    """Generic Exception for distro modules."""


class IpaTestException(IpaException):
    """Test subcommand exception."""


class IpaUtilsException(IpaException):
    """Generic exception for ipa utility methods."""


class IpaSSHException(IpaUtilsException):
    """Generic exception for ipa SSH methods."""
