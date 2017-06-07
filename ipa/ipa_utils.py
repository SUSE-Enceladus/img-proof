"""Utility methods."""
# -*- coding: utf-8 -*-
#
# Copyright (c) 2017 SUSE LLC
#
# This file is part of ipa.
#
# See LICENSE for license information.

try:
    import configparser as ConfigParser
except ImportError:
    import ConfigParser

import fnmatch
import os
import random
import sys
import time
from contextlib import contextmanager
from string import ascii_lowercase
from tempfile import NamedTemporaryFile

from ipa.ipa_constants import SYNC_POINTS
from ipa.ipa_exceptions import IpaSSHException, IpaUtilsException

import paramiko

import yaml

CLIENT_CACHE = {}


def clear_cache(ip=None):
    """Clear the client cache or remove key matching the given ip."""
    if ip:
        with ignored(KeyError):
            del CLIENT_CACHE[ip]
    else:
        CLIENT_CACHE.clear()


def establish_ssh_connection(ip,
                             ssh_private_key,
                             ssh_user,
                             port,
                             attempts=5,
                             timeout=None):
    """
    Establish ssh connection and return paramiko client.

    Raises:
        IpaProviderException: If connection cannot be established
            in given number of attempts.

    """
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.load_system_host_keys()

    while attempts:
        try:
            client.connect(
                ip,
                port=port,
                username=ssh_user,
                key_filename=ssh_private_key,
                timeout=timeout
            )
        except:
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
        if err:
            raise IpaSSHException(err)
        out = stdout.read()
    except:
        raise
    return out


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
    except:
        test_name, test_case = name, None

    path = tests.get(test_name, None)
    if not path:
        raise IpaUtilsException(
            'Test file with name: %s cannot be found.' % test_name
        )

    if test_case:
        path = ''.join([path, '::', test_case])
    return path


def get_config(config_path):
    """Parse ini config file."""
    if not os.path.isfile(config_path):
        raise IpaUtilsException(
            'Config file not found: %s' % config_path
        )

    config = ConfigParser.ConfigParser()
    try:
        result = config.read(config_path)
        if not result:
            raise
    except:
        raise IpaUtilsException(
            'Error parsing config file: %s' % config_path
        )

    return config


def get_from_config(config, section, default_section, entry):
    """Retrieve an entry from the configuration."""
    value = None
    with ignored(ConfigParser.Error):
        value = config.get(section, entry)

    if not value:
        try:
            value = config.get(default_section, entry)
        except ConfigParser.Error:
            raise IpaUtilsException(
                'Unable to get %s value from config' % entry
            )
    return value


def get_random_string(length=12):
    """Create random string of length with ascii lowercase chars."""
    return ''.join(random.choice(ascii_lowercase) for index in range(length))


def get_ssh_client(ip,
                   ssh_private_key,
                   ssh_user='root',
                   port=22,
                   attempts=3,
                   timeout=10):
    """Attempt to establish and test ssh connection."""
    if ip in CLIENT_CACHE:
        return CLIENT_CACHE[ip]

    client = None
    while attempts:
        try:
            client = establish_ssh_connection(
                ip,
                ssh_private_key,
                ssh_user,
                port,
                timeout=timeout
            )
            execute_ssh_command(client, 'ls')
        except:
            if client:
                client.close()
            attempts -= 1
            timeout += timeout
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
        config = yaml.load(f)
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
def ssh_config(ssh_user, ssh_private_key):
    """Create temporary ssh config file."""
    try:
        ssh_file = NamedTemporaryFile(delete=False)
        ssh_file.write('Host *\n')
        ssh_file.write('    IdentityFile %s\n' % ssh_private_key)
        ssh_file.write('    User %s' % ssh_user)
        ssh_file.close()
        yield ssh_file.name
    finally:
        with ignored(OSError):
            os.remove(ssh_file.name)
