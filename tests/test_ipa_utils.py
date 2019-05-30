#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""img_proof utils unit tests."""

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
import time

import paramiko
import pytest

from shutil import copyfile
from tempfile import NamedTemporaryFile

from img_proof import ipa_utils
from img_proof.ipa_exceptions import IpaSSHException, IpaUtilsException

from unittest.mock import MagicMock, patch

LOCALHOST = '127.0.0.1'


@patch('img_proof.ipa_utils.execute_ssh_command')
def test_utils_clear_cache(mock_exec_cmd):
    """Test img_proof utils client cache and clear specific ip."""
    client = MagicMock()
    ipa_utils.CLIENT_CACHE[LOCALHOST] = client

    val = ipa_utils.get_ssh_client(LOCALHOST, 'tests/data/ida_test')
    assert client == val

    # Test clear specfic IP
    ipa_utils.clear_cache(LOCALHOST)
    with pytest.raises(KeyError):
        ipa_utils.CLIENT_CACHE[LOCALHOST]

    ipa_utils.CLIENT_CACHE[LOCALHOST] = client

    # Test clear all cache
    ipa_utils.clear_cache()
    with pytest.raises(KeyError):
        ipa_utils.CLIENT_CACHE[LOCALHOST]


@patch.object(paramiko.SSHClient, 'exec_command')
@patch.object(paramiko.SSHClient, 'connect')
def test_utils_get_ssh_connection(mock_connect, mock_exec_cmd):
    """Test successful ssh connection."""
    stdin = stdout = stderr = MagicMock()
    stderr.read.return_value = b''

    mock_connect.return_value = None
    mock_exec_cmd.return_value = (stdin, stdout, stderr)

    ipa_utils.get_ssh_client(LOCALHOST, 'tests/data/ida_test')
    assert mock_connect.call_count == 1
    assert mock_exec_cmd.call_count == 1

    # Clear cache for subsequent tests.
    ipa_utils.clear_cache()


@patch.object(time, 'time')
@patch.object(time, 'sleep')
@patch.object(paramiko.SSHClient, 'connect')
def test_utils_ssh_connect_exception(mock_connect, mock_sleep, mock_time):
    """Test exception raised connecting to ssh."""
    mock_connect.side_effect = paramiko.ssh_exception.SSHException('ERROR!')
    mock_sleep.return_value = None
    mock_time.side_effect = [0, 0, 2]

    with pytest.raises(IpaSSHException) as error:
        ipa_utils.get_ssh_client(
            LOCALHOST,
            'tests/data/ida_test',
            timeout=1
        )

    assert str(error.value) == 'Attempt to establish SSH connection failed.'
    assert mock_connect.call_count > 0


def test_utils_ssh_exec_command():
    """Test successful command execution."""
    stdin = MagicMock()
    stdin.read.return_value = ''

    stderr = MagicMock()
    stderr.read.return_value = ''

    stdout = MagicMock()
    stdout.read.return_value = b'test test.sh'

    client = MagicMock()
    client.exec_command.return_value = (stdin, stdout, stderr)

    out = ipa_utils.execute_ssh_command(client, 'ls')
    assert out == 'test test.sh'


def test_utils_ssh_exec_command_exception():
    """Test error in ssh exec command raises exception."""
    stdin = MagicMock()

    stderr = MagicMock()
    stderr.read.return_value = b'Exception: ls is not allowed!'

    stdout = MagicMock()
    stdout.read.return_value = b'Other information\n'

    client = MagicMock()
    client.exec_command.return_value = (stdin, stdout, stderr)

    with pytest.raises(IpaSSHException) as error:
        ipa_utils.execute_ssh_command(client, 'ls')

    msg = 'Other information\nException: ls is not allowed!'
    assert str(error.value) == msg


def test_utils_expand_test_files():
    """Test expand test files utils function."""
    test_dirs = ['tests/data/tests']
    names = ['test_sles::test_sles', 'test_image_desc']
    expanded = ipa_utils.expand_test_files(test_dirs, names)
    assert expanded[0] - set(
        ['tests/data/tests/test_image.py',
         'tests/data/tests/test_sles.py::test_sles']
    ) == set()


def test_utils_test_file_not_found():
    """Test expand test file does not exist raises exception."""
    test_dirs = ['tests/data/tests']
    names = ['test_fake']

    with pytest.raises(IpaUtilsException) as error:
        ipa_utils.expand_test_files(test_dirs, names)

    assert str(error.value) == \
        'Test file with name: test_fake cannot be found.'


def test_utils_expand_names_not_list():
    """Test exception raised if names not a list."""
    test_dirs = ['tests/data/tests']
    names = 'test_sles'

    with pytest.raises(IpaUtilsException) as error:
        ipa_utils.expand_test_files(test_dirs, names)
    assert str(error.value) == \
        'Names must be a list containing test names and/or test descriptions.'


def test_utils_expand_sync_points():
    """Test expand test files with sync points."""
    test_dirs = ['tests/data/tests']
    names = ['test_soft_reboot', 'test_sles_desc', 'test_hard_reboot']
    expanded = ipa_utils.expand_test_files(test_dirs, names)

    assert len(expanded) == 3
    assert expanded[0] == 'test_soft_reboot'
    assert expanded[1] - set(
        ['tests/data/tests/test_sles.py',
         'tests/data/tests/test_image.py']
    ) == set()
    assert expanded[2] == 'test_hard_reboot'


@patch('img_proof.ipa_utils.execute_ssh_command')
def test_utils_extract_archive(mock_exec_ssh_command):
    client = MagicMock()

    mock_exec_ssh_command.return_value = 'archive successfully extracted!'

    # Test gzip
    ipa_utils.extract_archive(client, 'archive.tar.gz', extract_path='/tmp/')
    mock_exec_ssh_command.assert_called_once_with(
        client, 'tar -xf archive.tar.gz -C /tmp/'
    )
    mock_exec_ssh_command.reset_mock()


def test_utils_duplicate_files():
    """Test exception raised if duplicate test files exist."""
    test_dirs = ['tests/data/tests', 'tests/data/tests2']

    with pytest.raises(IpaUtilsException) as error:
        tests, descriptions = ipa_utils.get_test_files(test_dirs)
    assert (
        'Duplicate test file name found: '
        'tests/data/tests2/test_image.py, tests/data/tests/test_image.py' in
        str(error.value)
    )


def test_utils_file_description_overlap():
    """Test exception raised if test file and test description share name."""
    test_dirs = ['tests/data/tests3']

    with pytest.raises(IpaUtilsException) as error:
        tests, descriptions = ipa_utils.get_test_files(test_dirs)
    assert (
        'Test description name matches test file: '
        'tests/data/tests3/test_image.yaml, tests/data/tests3/test_image.py' in
        str(error.value)
    )


def test_utils_duplicate_test_description():
    """Test exception raised if duplicate test description."""
    test_dirs = ['tests/data/tests', 'tests/data/tests4']

    with pytest.raises(IpaUtilsException) as error:
        tests, descriptions = ipa_utils.get_test_files(test_dirs)
    assert (
        'Duplicate test description file name found: '
        'tests/data/tests4/test_image_desc.yaml, '
        'tests/data/tests/test_image_desc.yaml' in
        str(error.value)
    )


def test_get_config_values():
    """Test utils get config values function."""
    data = ipa_utils.get_config_values(
        'tests/data/config',
        'ec2',
        'img_proof'
    )

    assert data['region'] == 'us-west-1'
    assert data['test_dirs'] == 'tests/data/tests'


def test_utils_get_config_values_exceptions():
    """Test utils get config values function invalid path."""
    with pytest.raises(IpaUtilsException) as error:
        ipa_utils.get_config_values(
            'tests/data/fake.config',
            'ec2',
            'img_proof'
        )

    assert str(error.value) == \
        'Config file not found: tests/data/fake.config'


def test_utils_get_host_key_fingerprint():
    """Test get host key fingerprint function."""
    client = MagicMock()
    transport = MagicMock()
    key = MagicMock()

    client.get_transport.return_value = transport
    transport.get_remote_server_key.return_value = key
    key.get_fingerprint.return_value = b'\x04\x82\x04\x82'

    assert ipa_utils.get_host_key_fingerprint(client) == b'04820482'


def test_utils_get_random_string():
    """Test get random string function returns default len 12 string."""
    rand_string = ipa_utils.get_random_string()
    assert len(rand_string) == 12
    assert isinstance(rand_string, str)


def test_utils_put_file():
    client = MagicMock()
    sftp_client = MagicMock()
    client.open_sftp.return_value = sftp_client

    source_file = '/home/user/temp.file'
    destination_file = 'temp.file'

    ipa_utils.put_file(client, source_file, destination_file)

    sftp_client.put.assert_called_once_with(source_file, destination_file)
    sftp_client.close.assert_called_once_with()


def test_utils_redirect_output():
    """Test redirect output context manager."""
    temp_file = NamedTemporaryFile(mode='w+', delete=False)

    with ipa_utils.redirect_output(temp_file):
        print('Test message to file!')

    with open(temp_file.name) as temp_file:
        assert temp_file.readline() == 'Test message to file!\n'

    with ipa_utils.ignored(OSError):
        os.remove(temp_file.name)


def test_utils_ssh_config_context_mgr():
    """Test ssh config context manager function."""
    with ipa_utils.ssh_config('root', 'tests/data/ida_test') as conf:
        assert os.path.isfile(conf)
        with open(conf, 'r') as conf_file:
            assert conf_file.readline() == 'Host *\n'
            assert conf_file.readline() == \
                '    IdentityFile tests/data/ida_test\n'
            assert conf_file.readline() == '    User root'

    assert not os.path.isfile(conf)


def test_utils_history_log():
    """Test utils history log function."""
    history_file = NamedTemporaryFile(delete=False)
    history_file.close()

    copyfile('tests/data/.history', history_file.name)

    ipa_utils.update_history_log(
        history_file.name,
        test_log='tests/data/history.log'
    )

    with open(history_file.name, 'r+') as f:
        lines = f.readlines()

    assert lines[-1].strip() == 'tests/data/history.log'

    with ipa_utils.ignored(OSError):
        os.remove(history_file.name)


def test_utils_history_log_no_input():
    """Test utils history log function raises if no input."""
    with pytest.raises(IpaUtilsException) as error:
        ipa_utils.update_history_log('tests/data/.history')

    assert str(error.value) == \
        'A test log or clear flag must be provided.'


def test_utils_generate_instance_name():
    """Test generate instance name method."""
    name = ipa_utils.generate_instance_name('azure-img-proof-test')
    assert len(name) == 26
    assert name.startswith('azure-img-proof-test-')
