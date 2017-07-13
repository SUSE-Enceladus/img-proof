# -*- coding: utf-8 -*-

"""ipa constants."""

# Copyright (c) 2017 SUSE LLC
#
# This file is part of ipa.
#
# See LICENSE for license information.

import os


HOME = os.path.expanduser('~')
NOT_IMPLEMENTED = 'Implement method in child classes.'
SUPPORTED_DISTROS = ('openSUSE_Leap', 'SLES')
SUPPORTED_PROVIDERS = ('Azure', 'EC2', 'GCE')

AZURE_DEFAULT_TYPE = 'Small'
AZURE_DEFAULT_USER = 'azureuser'
EC2_DEFAULT_TYPE = 't2.micro'
EC2_DEFAULT_USER = 'ec2-user'

EC2_CONFIG_FILE = os.path.join(HOME, '.ec2utils.conf')
IPA_CONFIG_FILE = os.path.join(HOME, '.config', 'ipa', 'config')

IPA_HISTORY_FILE = os.path.join(HOME, '.config', 'ipa', '.history')
IPA_RESULTS_PATH = os.path.join(HOME, 'ipa', 'results')

SYNC_POINTS = (
    'test_hard_reboot',
    'test_soft_reboot',
    'test_update'
)

TEST_PATHS = (
    os.path.join(os.sep, 'usr', 'share', 'lib', 'ipa', 'tests', ''),
    os.path.join(HOME, 'ipa', 'tests', '')
)
