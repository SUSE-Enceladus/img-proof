# -*- coding: utf-8 -*-
#
# Copyright (c) 2017 SUSE LLC
#
# This file is part of ipa.
#
# See LICENSE for license information.

try:
    from configparser import ConfigParser
except ImportError:
    from ConfigParser import ConfigParser

import paramiko
import os
import sys
import time

from contextlib import contextmanager
from ipa_exceptions import IpaProviderException


def execute_ssh_command(cmd, client):
    """Execute given command using paramiko and return stdout, stderr."""
    try:
        stdin, stdout, stderr = client.exec_command(cmd)
        out = stdout.read()
        err = stderr.read()
    except:
        raise
    return out, err


def get_config(config_path):
    """Parse ipa ini config file."""
    if not os.path.isfile(config_path):
        raise IpaProviderException(
            'ipa config file not found: %s' % config_path
        )

    config = ConfigParser()
    config.read(config_path)
    return config


def get_ssh_client():
    """Return an instance of paramiko SSHClient."""
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.load_system_host_keys()
    return client


@contextmanager
def redirect_output(fileobj):
    """Redirect standard out to file."""
    old = sys.stdout
    sys.stdout = fileobj
    try:
        yield fileobj
    finally:
        sys.stdout = old


def ssh_connect(client,
                ip,
                ssh_private_key,
                ssh_user,
                port,
                attempts=30,
                timeout=None):
    """Establish ssh connection and return paramiko client.

    If connection cannot be established in given number of attempts
    raise IpaProviderException.
    """
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
            return 0

    raise IpaProviderException(
        'Failed to establish SSH connection to instance.'
    )


@contextmanager
def ssh_connection(client,
                   ip,
                   ssh_private_key,
                   ssh_user='root',
                   port=22):
    """Redirect standard out to file."""
    try:
        wait_on_ssh_connection(
            client,
            ip,
            ssh_private_key,
            ssh_user,
            port
        )
        yield client
    except:
        print('Error!')
        raise
    finally:
        if client:
            client.close()


def wait_on_ssh_connection(client,
                           ip,
                           ssh_private_key,
                           ssh_user='root',
                           port=22,
                           attempts=3,
                           timeout=10):
    """Attempt to establish and test ssh connection."""
    while attempts:
        try:
            ssh_connect(
                client,
                ip,
                ssh_private_key,
                ssh_user,
                port,
                timeout=timeout
            )
            execute_ssh_command('ls', client)
        except:
            client.close()
            attempts -= 1
            timeout += timeout
        else:
            return 0

    raise IpaProviderException(
        'Attempt to establish SSH connection failed.'
    )
