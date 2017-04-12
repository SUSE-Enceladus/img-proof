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
import paramiko
import os
import random
import sys
import time
import yaml

from contextlib import contextmanager
from ipa_exceptions import IpaSSHException, IpaUtilsException
from tempfile import NamedTemporaryFile

CHARS = 'abcdefghijklmnopqrstuvwxyz'
CLIENT_CACHE = {}


def clear_cache(ip=None):
    """Cache the client connection with ip as key."""
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
    """Establish ssh connection and return paramiko client.

    If connection cannot be established in given number of attempts
    raise IpaProviderException.
    """
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.load_system_host_keys()

    sys.stdout.write('Establishing ssh connection.')
    sys.stdout.flush()
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
            # Print without new lines
            sys.stdout.write('.')
            sys.stdout.flush()
            attempts -= 1
            time.sleep(10)
        else:
            print('\nConnection established.\n')
            return client

    raise IpaSSHException(
        'Failed to establish SSH connection to instance.'
    )


def execute_ssh_command(client, cmd):
    """Execute given command using paramiko and return stdout, stderr."""
    try:
        stdin, stdout, stderr = client.exec_command(cmd)
        err = stderr.read()
        if err:
            raise IpaSSHException(err)
        out = stdout.read()
    except:
        raise
    return out


def find_test_files(roots, names):
    """Walk all dirs and find path of given test file names."""
    tests = {}
    for root_dir in roots:
        for root, dirs, files in os.walk(root_dir):
            matches = fnmatch.filter(files, 'test_*.py')
            for match in matches:
                if match not in tests:
                    tests[match] = (os.path.join(root, match))
                else:
                    raise IpaUtilsException(
                        'Duplicate test file found: %s' % match
                    )

    test_files = []
    for name in names:
        test_name = name.split('::', 1)
        if test_name[0] in tests:
            path = tests.get(test_name[0])
            if len(test_name) == 2:
                path = ''.join([path, '::', test_name[1]])
            test_files.append(path)
        else:
            raise IpaUtilsException(
                'Test file with name: %s cannot be found.' % test_name[0]
            )

    return list(set(test_files))


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
    """Retrieve an entry from the configuration"""
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


def get_random_string(length=12, allowed_chars=CHARS):
    """Create random string of length with allowed characters."""
    return ''.join(random.choice(allowed_chars) for _ in range(length))


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


def get_yaml_config(config_path):
    """Load yaml config file and return dictionary."""
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
