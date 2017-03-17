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


def get_config(config_path):
    """Parse ipa ini config file."""
    if not os.path.isfile(config_path):
        raise IpaProviderException(
            'ipa config file not found: %s' % config_path
        )

    config = ConfigParser()
    config.read(config_path)
    return config


@contextmanager
def redirect_output(fileobj):
    """Redirect standard out to file."""
    old = sys.stdout
    sys.stdout = fileobj
    try:
        yield fileobj
    finally:
        sys.stdout = old


def ssh_connect(ip, ssh_private_key, ssh_user, port, timeout=30):
    """Establish ssh connection and return paramiko client.

    If connection cannot be established prior to timeout raise
    IpaProviderException.
    """
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.load_system_host_keys()

    attempts = 0
    sys.stdout.write('Establishing ssh connection.')
    sys.stdout.flush()
    while attempts < timeout:
        try:
            client.connect(
                ip,
                port=port,
                username=ssh_user,
                key_filename=ssh_private_key
            )
        except:
            # Print without new lines
            sys.stdout.write('.')
            sys.stdout.flush()
            attempts += 1
            time.sleep(10)
        else:
            print('\nConnection established.\n')
            return client

    raise IpaProviderException(
        'Failed to establish SSH connection to instance.'
    )


def wait_on_ssh_connection(ip,
                           ssh_private_key,
                           ssh_user='root',
                           port=22,
                           timeout=30):
    """Attempt to establish an ssh connection."""
    client = None
    try:
        client = ssh_connect(ip, ssh_private_key, ssh_user, port, timeout)
    except IpaProviderException:
        raise
    finally:
        if client:
            client.close()


def execute_ssh_command(cmd, ip, ssh_private_key, ssh_user='root', port=22):
    """Execute given command using paramiko and return stdout, stderr."""
    client = None
    try:
        client = ssh_connect(ip, ssh_private_key, ssh_user, port)
        stdin, stdout, stderr = client.exec_command(cmd)
        out = stdout.read()
        err = stderr.read()
    except:
        raise
    finally:
        if client:
            client.close()
    return out, err
