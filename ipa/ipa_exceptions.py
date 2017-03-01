# -*- coding: utf-8 -*-
#
# Copyright (c) 2017 SUSE LLC
#
# This file is part of ipa.
#
# See LICENSE for license information.


class IpaProviderException(Exception):
    """Generic exception for the ipa package."""


class AzureProviderException(IpaException):
    """Generic Azure exception."""


class EC2ProviderException(IpaException):
    """Generic EC2 exception."""


class GCEProviderException(IpaException):
    """Generic GCE exception."""


class ImageNotFoundException(IpaException):
    """Exception for image not found on cloud provider."""


class InstanceException(IpaException):
    """Generic exception for the framework instance methods."""


class ListTestsException(IpaException):
    """List subcommand exception."""


class ResultsException(IpaExcception):
    """Results subcommand exception."""


class TestException(IpaException):
    """Test subcommand exception."""

