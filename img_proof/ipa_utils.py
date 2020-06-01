# -*- coding: utf-8 -*-

"""Utility functions."""

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

import configparser
import fnmatch
import os
import random
import sys
import time

import paramiko
import yaml

from binascii import hexlify
from contextlib import contextmanager
from string import ascii_lowercase
from tempfile import NamedTemporaryFile

from img_proof.ipa_constants import SYNC_POINTS
from img_proof.ipa_exceptions import IpaSSHException, IpaUtilsException

CLIENT_CACHE = {}


def clear_cache(ip=None):
    """Clear the client cache or remove key matching the given ip."""
    if ip:
        with ignored(Exception):
            client = CLIENT_CACHE[ip]
            del CLIENT_CACHE[ip]
            client.close()
    else:
        for client in CLIENT_CACHE.values():
            with ignored(Exception):
                client.close()
        CLIENT_CACHE.clear()


def establish_ssh_connection(ip,
                             ssh_private_key_file,
                             ssh_user,
                             port,
                             attempts=5,
                             timeout=None):
    """
    Establish ssh connection and return paramiko client.

    Raises:
        IpaSSHException: If connection cannot be established
            in given number of attempts.
    """
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    while attempts:
        try:
            client.connect(
                ip,
                port=port,
                username=ssh_user,
                key_filename=ssh_private_key_file,
                timeout=timeout
            )
        except:  # noqa: E722
            attempts -= 1
            time.sleep(10)
        else:
            return client

    raise IpaSSHException(
        'Failed to establish SSH connection to instance.'
    )


def execute_ssh_command(client, cmd):
    """
    Execute given command using paramiko.

    Returns:
        String output of cmd execution.
    Raises:
        IpaSSHException: If stderr returns a non-empty string.
    """
    try:
        stdin, stdout, stderr = client.exec_command(cmd)
        err = stderr.read()
        out = stdout.read()
        if err:
            raise IpaSSHException(out.decode() + err.decode())
    except:  # noqa: E722
        raise
    return out.decode()


def expand_test_files(test_dirs, names):
    """
    Expand the list of test files and test descriptions.

    The list is split on sync points and duplicates in
    each set are removed.

    Returns:
        List of test files split into sets by sync points.
    Raises:
        IpaUtilsException: If names is not a list.
    """
    if not isinstance(names, list):
        raise IpaUtilsException(
            'Names must be a list containing test names'
            ' and/or test descriptions.'
        )

    tests, descriptions = get_test_files(test_dirs)

    expanded_names = []
    for name in names:
        if name in descriptions:
            expanded_names += get_tests_from_description(
                name,
                descriptions
            )
        else:
            expanded_names.append(name)

    return parse_sync_points(expanded_names, tests)


def extract_archive(client, archive_path, extract_path=None):
    """
    Extract the archive in current path using the provided client.

    If extract_path is provided extract the archive there.
    """
    command = 'tar -xf {path}'.format(path=archive_path)

    if extract_path:
        command += ' -C {extract_path}'.format(extract_path=extract_path)

    out = execute_ssh_command(client, command)
    return out


def find_test_file(name, tests):
    """
    Find test file by name, given a list of tests.

    If a specific test case is appended to test
    name, split the case and append to path.

    Raises:
        IpaUtilsException: If test file not found.
    """
    try:
        test_name, test_case = name.split('::', 1)
    except ValueError:
        test_name, test_case = name, None

    path = tests.get(test_name, None)
    if not path:
        raise IpaUtilsException(
            'Test file with name: %s cannot be found.' % test_name
        )

    if test_case:
        path = ''.join([path, '::', test_case])
    return path


def generate_instance_name(name):
    """Generate a new random name for instance."""
    return '%s-%s' % (name, get_random_string(length=5))


def get_public_ssh_key(ssh_private_key_file):
    """Get SSH public key from private key file."""
    pub_key = ssh_private_key_file + '.pub'

    try:
        with open(pub_key, "rb") as key_file:
            key = key_file.read()
    except FileNotFoundError:
        raise IpaUtilsException(
            'SSH public key file: {key_path} cannot be found.'.format(
                key_path=pub_key
            )
        )

    return key


def get_config_values(config_path, section, default='default'):
    """
    Parse ini config file and return a dict of values.

    The provided section overrides any values in default section.
    """
    values = {}

    if not os.path.isfile(config_path):
        raise IpaUtilsException(
            'Config file not found: %s' % config_path
        )

    config = configparser.ConfigParser()

    try:
        config.read(config_path)
    except Exception:
        raise IpaUtilsException(
            'Config file format invalid.'
        )

    try:
        values.update(config.items(default))
    except Exception:
        pass

    try:
        values.update(config.items(section))
    except Exception:
        pass

    return values


def get_host_key_fingerprint(client):
    """Get host key fingerprint of SSH client."""
    return hexlify(
        client.get_transport().get_remote_server_key().get_fingerprint()
    )


def get_random_string(length=12):
    """Create random string of length with ascii lowercase chars."""
    return ''.join(random.choice(ascii_lowercase) for index in range(length))


def get_ssh_client(ip,
                   ssh_private_key_file,
                   ssh_user='root',
                   port=22,
                   timeout=600,
                   wait_period=10):
    """Attempt to establish and test ssh connection."""
    if CLIENT_CACHE.get(ip):
        try:
            execute_ssh_command(CLIENT_CACHE[ip], 'ls')
        except Exception:
            clear_cache(ip)
        else:
            return CLIENT_CACHE[ip]

    start = time.time()
    end = start + timeout

    client = None
    while time.time() < end:
        try:
            client = establish_ssh_connection(
                ip,
                ssh_private_key_file,
                ssh_user,
                port,
                timeout=wait_period
            )
            execute_ssh_command(client, 'ls')
        except:  # noqa: E722
            if client:
                client.close()
            wait_period += wait_period
        else:
            CLIENT_CACHE[ip] = client
            return client

    raise IpaSSHException(
        'Attempt to establish SSH connection failed.'
    )


def get_test_files(test_dirs):
    """
    Walk all test dirs and find all tests and test descriptions.

    Returns:
        A tuple containing a dict mapping test names to full path
        and a dict mapping test descriptions to full path.
    Raises:
        IpaUtilsException: If there are multiple test files or
            test descriptions with the same name. Or, if there is a
            name overlap with a test file and test description.
    """
    tests = {}
    descriptions = {}
    for test_dir in test_dirs:
        if not os.path.exists(test_dir):
            continue

        for root, dirs, files in os.walk(test_dir):
            test_files = fnmatch.filter(files, 'test_*.py')
            description_files = fnmatch.filter(files, 'test_*.yaml')

            for test_file in test_files:
                path = os.path.join(root, test_file)
                name, ext = test_file.split('.')
                if name not in tests:
                    tests[name] = path
                else:
                    raise IpaUtilsException(
                        'Duplicate test file name found: %s, %s'
                        % (path, tests.get(name))
                    )

            for description_file in description_files:
                path = os.path.join(root, description_file)
                name, ext = description_file.split('.')
                if name in tests:
                    raise IpaUtilsException(
                        'Test description name matches test file: %s, %s'
                        % (path, tests.get(name))
                    )
                elif name not in descriptions:
                    descriptions[name] = path
                else:
                    raise IpaUtilsException(
                        'Duplicate test description file name found: %s, %s'
                        % (path, descriptions.get(name))
                    )

    return tests, descriptions


def get_tests_from_description(name,
                               descriptions,
                               parsed=None):
    """
    Recursively collect all tests in test description.

    Args:
        name (str): Yaml test description file name.
        descriptions (dict): Dict of test description name
                             (key) and absolute file paths
                             (value).
        parsed (list): List of description paths which have
                       already been parsed to prevent infinte
                       recursion.
    Returns:
        A list of expanded test files.
    """
    tests = []
    if not parsed:
        parsed = []

    description = descriptions.get(name, None)
    if not description:
        raise IpaUtilsException(
            'Test description file with name: %s cannot be located.'
            % name
        )

    if description in parsed:
        return tests

    parsed.append(description)
    test_data = get_yaml_config(description)

    if 'tests' in test_data:
        tests += test_data.get('tests')

    if 'include' in test_data:
        for description_name in test_data.get('include'):
            tests += get_tests_from_description(
                description_name,
                descriptions,
                parsed
            )

    return tests


def get_yaml_config(config_path):
    """
    Load yaml config file and return dictionary.

    Todo:
        * This will need refactoring similar to the test search.
    """
    config_path = os.path.expanduser(config_path)
    if not os.path.isfile(config_path):
        raise IpaUtilsException(
            'Config file not found: %s' % config_path
        )

    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    return config


@contextmanager
def ignored(*exceptions):
    """Ignore the provided exception(s)."""
    try:
        yield
    except exceptions:
        pass


def parse_sync_points(names, tests):
    """
    Slice list of test names on sync points.

    If test is test file find full path to file.

    Returns:
        A list of test file sets and sync point strings.
    Examples:
        ['test_hard_reboot']
        [set('test1', 'test2')]
        [set('test1', 'test2'), 'test_soft_reboot']
        [set('test1', 'test2'), 'test_soft_reboot', set('test3')]
    """
    test_files = []
    section = set()

    for name in names:
        if name in SYNC_POINTS:
            if section:
                test_files.append(section)

            test_files.append(name)
            section = set()
        else:
            section.add(find_test_file(name, tests))

    if section:
        test_files.append(section)
    return test_files


def parse_test_name(name):
    """Parse and return formatted pytest test name string."""
    test_class = None
    if '::' in name:
        try:
            path, test_class, parens, test_case = name.split('::')
        except ValueError:
            path, test_case = name.split('::')

        test_file = path.split(os.sep)[-1].replace('.py', '')
        return '::'.join(filter(None, [test_file, test_class, test_case]))
    else:
        return name


def put_file(client, source_file, destination_file):
    """
    Copy file to instance using Paramiko client connection.
    """
    try:
        sftp_client = client.open_sftp()
        sftp_client.put(source_file, destination_file)
    except Exception as error:
        raise IpaUtilsException(
            'Error copying file to instance: {0}.'.format(error)
        )
    finally:
        with ignored(Exception):
            sftp_client.close()


@contextmanager
def redirect_output(fileobj):
    """Redirect standard out to file."""
    old = sys.stdout
    sys.stdout = fileobj
    try:
        yield fileobj
    finally:
        sys.stdout = old


@contextmanager
def ssh_config(ssh_user, ssh_private_key_file):
    """Create temporary ssh config file."""
    try:
        ssh_file = NamedTemporaryFile(delete=False, mode='w+')
        ssh_file.write('Host *\n')
        ssh_file.write('    IdentityFile %s\n' % ssh_private_key_file)
        ssh_file.write('    User %s' % ssh_user)
        ssh_file.close()
        yield ssh_file.name
    finally:
        with ignored(OSError):
            os.remove(ssh_file.name)


def update_history_log(history_log,
                       clear=False,
                       description=None,
                       test_log=None):
    """
    Update the history log file with item.
    If clear flag is provided the log file is deleted.
    """
    if not test_log and not clear:
        raise IpaUtilsException(
            'A test log or clear flag must be provided.'
        )

    if clear:
        with ignored(OSError):
            os.remove(history_log)

    else:
        history_dir = os.path.dirname(history_log)
        if not os.path.isdir(history_dir):
            try:
                os.makedirs(history_dir)
            except OSError as error:
                raise IpaUtilsException(
                    'Unable to create directory: %s' % error
                )

        with open(history_log, 'a+') as f:
            # Using append mode creates file if it does not exist
            if description:
                description = '"%s"' % description

            out = '{} {}'.format(
                test_log,
                description or ''
            )
            f.write(out.strip() + '\n')
