# -*- coding: utf-8 -*-

"""img_proof constants."""

# Copyright (c) 2019 SUSE LLC. All rights reserved.
#
# This file is part of img_proof. img_proof provides an api and command line
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

import os


HOME = os.path.expanduser('~')
NOT_IMPLEMENTED = 'Implement method in child classes.'
SUPPORTED_DISTROS = ('opensuse_leap', 'sles')
SUPPORTED_CLOUDS = ('azure', 'ec2', 'gce', 'ssh', 'oci')

AZURE_DEFAULT_TYPE = 'Standard_B1ms'
AZURE_DEFAULT_USER = 'azureuser'
EC2_DEFAULT_TYPE = 't2.micro'
EC2_DEFAULT_USER = 'ec2-user'
GCE_DEFAULT_TYPE = 'n1-standard-1'
GCE_DEFAULT_USER = 'root'
OCI_DEFAULT_TYPE = 'VM.Standard2.1'
OCI_DEFAULT_USER = 'opc'

EC2_CONFIG_FILE = os.path.join(HOME, '.ec2utils.conf')
IPA_CONFIG_FILE = os.path.join(HOME, '.config', 'img_proof', 'config')

IPA_HISTORY_FILE = os.path.join(HOME, '.config', 'img_proof', '.history')
IPA_RESULTS_PATH = os.path.join(HOME, 'img_proof', 'results')

BASH_SSH_SCRIPT = '''#!/bin/bash
echo {key} >> /home/{user}/.ssh/authorized_keys
'''

SYNC_POINTS = (
    'test_hard_reboot',
    'test_soft_reboot',
    'test_update',
    'test_refresh'
)

TEST_PATHS = (
    os.path.join(os.sep, 'usr', 'share', 'lib', 'img_proof', 'tests', ''),
    os.path.join(HOME, 'img_proof', 'tests', '')
)
