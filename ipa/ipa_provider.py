# -*- coding: utf-8 -*-

"""Base provider class for testing cloud images."""

# Copyright (c) 2017 SUSE LLC
#
# This file is part of ipa. Ipa provides an api and command line
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

import json
import logging
import os
import shlex
import time

import pytest

from collections import defaultdict
from datetime import datetime

from ipa import ipa_utils
from ipa.ipa_constants import (
    IPA_CONFIG_FILE,
    IPA_HISTORY_FILE,
    IPA_RESULTS_PATH,
    NOT_IMPLEMENTED,
    TEST_PATHS
)
from ipa.ipa_opensuse_leap import openSUSE_Leap
from ipa.ipa_sles import SLES
from ipa.ipa_exceptions import (
    IpaException,
    IpaProviderException,
    IpaSSHException,
    IpaUtilsException
)
from ipa.results_plugin import Report


class IpaProvider(object):
    """
    Base provider class.

    Provides methods for testing images. Cloud provider
    modules extend the base class and implement cloud
    specific methods for launching and managing instances.
    """

    def __init__(self,
                 provider,
                 cleanup=None,
                 config=None,
                 description=None,
                 distro_name=None,
                 early_exit=None,
                 history_log=None,
                 image_id=None,
                 inject=None,
                 instance_type=None,
                 log_level=None,
                 no_default_test_dirs=False,
                 provider_config=None,
                 region=None,
                 results_dir=None,
                 running_instance_id=None,
                 test_dirs=None,
                 test_files=None,
                 timeout=None,
                 collect_vm_info=None):
        """Initialize base provider class."""
        super(IpaProvider, self).__init__()
        log_level = log_level or logging.INFO
        self.logger = logging.getLogger('ipa')
        self.logger.setLevel(log_level)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        console_handler.setFormatter(logging.Formatter('%(message)s'))

        self.logger.addHandler(console_handler)

        # Get ipa ini config file
        self.config = config or IPA_CONFIG_FILE

        try:
            self.ipa_config = ipa_utils.get_config(self.config)
            self.logger.debug('Using ipa config file: %s' % self.config)
        except IpaException:
            self.ipa_config = None
            self.logger.debug('IPA config file not found: %s' % self.config)

        self.description = description
        self.host_key_fingerprint = None
        self.instance_ip = None
        self.provider = provider
        self.collect_vm_info = self._get_value(
            collect_vm_info,
            config_key='collect_vm_info',
            default=False
        )

        self.cleanup = self._get_value(cleanup)
        self.distro_name = self._get_value(distro_name)
        self.early_exit = self._get_value(early_exit)
        self.image_id = self._get_value(image_id)
        self.inject = self._get_value(inject)
        self.instance_type = self._get_value(instance_type)
        self.running_instance_id = self._get_value(running_instance_id)
        self.test_files = list(self._get_value(test_files, default=[]))
        self.timeout = self._get_value(
            timeout,
            config_key='timeout',
            default=600
        )

        self.history_log = self._get_value(
            history_log,
            config_key='history_log',
            default=IPA_HISTORY_FILE
        )

        self.provider_config = self._get_value(
            provider_config,
            config_key='provider_config'
        )
        if self.provider_config:
            self.provider_config = os.path.expanduser(self.provider_config)

        self.region = self._get_value(
            region,
            config_key='region'
        )

        self.results = {
            "tests": [],
            "summary": defaultdict(
                int,
                {"duration": 0, "passed": 0, "num_tests": 0}
            )
        }

        self.results_dir = os.path.expanduser(
            self._get_value(
                results_dir,
                config_key='results_dir',
                default=IPA_RESULTS_PATH
            )
        )

        if not self.distro_name:
            raise IpaProviderException(
                'Distro name is required.'
            )
        else:
            self.distro_name = self.distro_name.lower()

        if self.provider != 'ssh':
            if not self.image_id and not self.running_instance_id:
                raise IpaProviderException(
                    'Image ID or running instance is required.'
                )

        self._parse_test_files(test_dirs, no_default_test_dirs)

    def _get_instance(self):
        raise NotImplementedError(NOT_IMPLEMENTED)

    def _get_instance_state(self):
        raise NotImplementedError(NOT_IMPLEMENTED)

    def _get_ssh_client(self):
        """Return a new or existing SSH client for given ip."""
        return ipa_utils.get_ssh_client(
            self.instance_ip,
            self.ssh_private_key_file,
            self.ssh_user,
            timeout=self.timeout
        )

    def _get_value(self, arg, config_key=None, default=None):
        """Return the correct value for the given arg."""
        value = default

        if arg or arg is False:
            value = arg

        elif config_key and self.ipa_config:
            with ipa_utils.ignored(IpaUtilsException):
                value = ipa_utils.get_from_config(
                    self.ipa_config,
                    self.provider,
                    'ipa',
                    config_key
                )

        return value

    def _is_instance_running(self):
        raise NotImplementedError(NOT_IMPLEMENTED)

    def _launch_instance(self):
        raise NotImplementedError(NOT_IMPLEMENTED)

    def _log_info(self):
        """Output test run information to top of log file."""
        if self.provider == 'ssh':
            self.results['info'] = {
                'platform': self.provider,
                'distro': self.distro_name,
                'image': self.instance_ip,
                'timestamp': self.time_stamp,
                'log_file': self.log_file,
                'results_file': self.results_file
            }
        else:
            self.results['info'] = {
                'platform': self.provider,
                'region': self.region,
                'distro': self.distro_name,
                'image': self.image_id,
                'instance': self.running_instance_id,
                'timestamp': self.time_stamp,
                'log_file': self.log_file,
                'results_file': self.results_file
            }

        with open(self.log_file, 'a') as log_file:
            log_file.write(
                '\n'.join(
                    '%s: %s' % (key, val) for key, val
                    in self.results['info'].items()
                )
            )
            log_file.write('\n')

    def _merge_results(self, results):
        """Combine results of test run with exisiting dict."""
        self.results['tests'] += results['tests']

        for key, value in results['summary'].items():
            self.results['summary'][key] += value

    def _parse_test_files(self, test_dirs, no_default_test_dirs):
        """
        Collect all test dirs and expand test files.

        The test files are expanded to absolute paths given
        test names and a list of availble test dirs to use.
        """
        self.test_dirs = set()
        if test_dirs:
            # Command line arg
            self.test_dirs.update(test_dirs.split(','))

        with ipa_utils.ignored(IpaUtilsException):
            if self.ipa_config:
                # ipa config arg
                test_dirs = ipa_utils.get_from_config(
                    self.ipa_config,
                    self.provider,
                    'ipa',
                    'test_dirs'
                )

                if test_dirs:
                    self.test_dirs.update(test_dirs.split(','))

        if not no_default_test_dirs:
            self.test_dirs.update(TEST_PATHS)

        # Confirm all test dir paths are absolute, unique and
        # normalized (remove redundant slashes .../ ...// etc.)
        self.test_dirs = set(
            os.path.normpath(
                os.path.expanduser(test_dir)
            ) for test_dir in self.test_dirs
        )

        if not self.test_dirs:
            raise IpaProviderException(
                'At least one test directory is required.'
            )

        self.test_files = ipa_utils.expand_test_files(
            self.test_dirs,
            self.test_files
        )

    def _process_test_results(self, duration, test_name, success=0):
        """Create result dict for sync test and merge with overall results."""
        status = 'passed' if success == 0 else 'failed'
        result = {
            'tests': [
                {
                    'outcome': status,
                    'test_index': 0,
                    'name': test_name
                }
            ],
            'summary': {
                'duration': duration,
                status: 1,
                'num_tests': 1
            }
        }
        self._merge_results(result)

    def _run_tests(self, tests, ssh_config):
        """Run the test suite on the image."""
        options = []
        if self.early_exit:
            options.append('-x')

        args = '-v {} --ssh-config={} --hosts={} {}'.format(
                ' '.join(options),
                ssh_config,
                self.instance_ip,
                ' '.join(tests)
            )

        # Print output captured to log file for test run
        print(
            '\nTest directories:\n{}\n'.format(
                '\n'.join(self.test_dirs)
            )
        )
        print('Arguments:\n{}\n'.format(args))

        cmds = shlex.split(args)
        plugin = Report()
        result = pytest.main(cmds, plugins=[plugin])

        # If pytest has an error there will be no report but
        # we still want to process the error as a failure.
        # https://docs.pytest.org/en/latest/usage.html#possible-exit-codes
        if result in (2, 3, 4):
            self._process_test_results(0, 'pytest_error', 1)
        else:
            self._merge_results(plugin.report)

        return result

    def _save_results(self):
        """Save results dictionary to json file."""
        with open(self.results_file, 'w') as results_file:
            json.dump(self.results, results_file)

    def _set_distro(self):
        """Determine distro for image and create instance of class."""
        if self.distro_name == 'sles':
            self.distro = SLES()
        elif self.distro_name == 'opensuse_leap':
            self.distro = openSUSE_Leap()
        else:
            raise IpaProviderException(
                'Distribution: %s, not supported.' % self.distro_name
            )

    def _set_image_id(self):
        raise NotImplementedError(NOT_IMPLEMENTED)

    def _set_instance_ip(self):
        raise NotImplementedError(NOT_IMPLEMENTED)

    def _set_results_dir(self):
        """Create results directory if not exists."""
        if self.running_instance_id:
            self.results_dir = os.path.join(
                self.results_dir,
                self.provider,
                self.image_id,
                self.running_instance_id
            )
        else:
            self.results_dir = os.path.join(
                self.results_dir,
                self.provider,
                self.instance_ip
            )

        try:
            os.makedirs(self.results_dir)
        except OSError as error:
            if not os.path.isdir(self.results_dir):
                raise IpaProviderException(
                    'Unable to create ipa results directory: %s' % error
                )

        self.time_stamp = datetime.now().strftime('%Y%m%d%H%M%S')
        self.log_file = ''.join(
            [self.results_dir, os.sep, self.time_stamp, '.log']
        )
        self.logger.debug('Created log file %s' % self.log_file)

        self.results_file = ''.join(
            [self.results_dir, os.sep, self.time_stamp, '.results']
        )
        self.logger.debug('Created results file %s' % self.results_file)

        # Add log file handler
        file_handler = logging.FileHandler(self.log_file)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(logging.Formatter('\n%(message)s\n'))
        self.logger.addHandler(file_handler)

    def _start_instance(self):
        """Start the instance."""
        raise NotImplementedError(NOT_IMPLEMENTED)

    def _start_instance_if_stopped(self):
        """Start instance if stopped."""
        if not self._is_instance_running():
            self.logger.info('Starting instance')
            self._start_instance()

    def _stop_instance(self):
        """Stop the instance."""
        raise NotImplementedError(NOT_IMPLEMENTED)

    def _terminate_instance(self):
        """Terminate the instance."""
        raise NotImplementedError(NOT_IMPLEMENTED)

    def _collect_vm_info(self):
        """
        Gather basic info about VM
        """
        try:
            self.logger.info('Collecting basic info about VM')
            client = self._get_ssh_client()
            self.logger.info('systemd-analyze :')
            self.execute_ssh_command(client, 'systemd-analyze')
            self.logger.info('systemd-analyze blame')
            self.execute_ssh_command(client, 'systemd-analyze blame')
            self.logger.info('journalctl -b : ')
            self.execute_ssh_command(client, 'sudo journalctl -b')
        except Exception as error:
            self.logger.info('Fail to collect VM info : {0}.'.format(error))

    def _update_history(self):
        """Save the current test information to history json."""
        ipa_utils.update_history_log(
            self.history_log,
            description=self.description,
            test_log=self.log_file
        )

    def _wait_on_instance(self, state, timeout=600, wait_period=10):
        """Wait until instance is in given state."""
        current_state = 'Undefined'
        start = time.time()
        end = start + timeout

        while time.time() < end:
            current_state = self._get_instance_state()

            if state == current_state:
                return

            time.sleep(wait_period)

        raise IpaProviderException(
            'Instance has not arrived at the given state: {state}'.format(
                state=state
            )
        )

    def execute_ssh_command(self, client, command):
        """Execute the provided command and log output."""
        try:
            out = ipa_utils.execute_ssh_command(client, command)
        except Exception as error:
            raise IpaProviderException(
                'Command: "{0}", failed execution: {1}.'.format(
                    command, error
                )
            )
        else:
            with open(self.log_file, 'a') as log_file:
                log_file.write('\n')
                log_file.write(out)

    def extract_archive(self, client, archive_path, extract_path=None):
        """Extract the archive files using the client in the current path."""
        try:
            out = ipa_utils.extract_archive(client, archive_path, extract_path)
        except Exception as error:
            raise IpaProviderException(
                'Failed to extract archive, "{0}": {1}.'.format(
                    archive_path, error
                )
            )

        else:
            with open(self.log_file, 'a') as log_file:
                log_file.write('\n')
                log_file.write(out)

    def hard_reboot_instance(self):
        """Stop then start the instance."""
        self._stop_instance()
        self._start_instance()
        self._set_instance_ip()
        self.logger.debug('IP of instance: %s' % self.instance_ip)
        ipa_utils.clear_cache()

    def install_package(self, client, package):
        """
        Install package using distro specific install method.
        """
        try:
            out = self.distro.install_package(client, package)
        except Exception as error:
            raise IpaProviderException(
                'Failed installing package, "{0}"; {1}.'.format(
                    package, error
                )
            )
        else:
            with open(self.log_file, 'a') as log_file:
                log_file.write('\n')
                log_file.write(out)

    def process_injection_file(self, client):
        """
        Load yaml file and process injection configuration.

        There are 5 injection options:

        :inject_packages: an rpm path or list of rpm paths which will be
                          copied and installed on the test instance.
        :inject_archives: an archive or list of archives which will
                          be copied and extracted on the test instance.
        :inject_files: a file path or list of file paths which
                       will be copied to the test instance.
        :execute: a command or list of commands to run on the test instance.
        :install: a package name or list of package names to
                 install from an existing repo on the test instance.

        The order of processing is as follows: inject_packages,
        inject_archives, inject_files, execute, install.
        """
        configuration = ipa_utils.get_yaml_config(self.inject)

        if configuration.get('inject_packages'):
            inject_packages = configuration['inject_packages']

            if not isinstance(inject_packages, list):
                inject_packages = [inject_packages]

            for package in inject_packages:
                package_path = self.put_file(client, package)
                self.install_package(client, package_path)

        if configuration.get('inject_archives'):
            inject_archives = configuration['inject_archives']

            if not isinstance(inject_archives, list):
                inject_archives = [inject_archives]

            for archive in inject_archives:
                archive_path = self.put_file(client, archive)
                self.extract_archive(client, archive_path)

        if configuration.get('inject_files'):
            inject_files = configuration['inject_files']

            if not isinstance(inject_files, list):
                inject_files = [inject_files]

            for file_path in inject_files:
                self.put_file(client, file_path)

        if configuration.get('execute'):
            execute = configuration['execute']

            if not isinstance(execute, list):
                execute = [execute]

            for command in execute:
                self.execute_ssh_command(client, command)

        if configuration.get('install'):
            install = configuration['install']

            if not isinstance(install, list):
                install = [install]

            for package in install:
                self.install_package(client, package)

    def put_file(self, client, source_file):
        """
        Put file on instance in default SSH directory.
        """
        try:
            file_name = os.path.basename(source_file)
            ipa_utils.put_file(client, source_file, file_name)
        except Exception as error:
            raise IpaProviderException(
                'Failed copying file, "{0}"; {1}.'.format(
                    source_file, error
                )
            )
        else:
            return file_name

    def test_image(self):
        """
        The entry point for testing an image.

        Creates new or initiates existing instance. Runs
        test suite on instance. Collects and returns
        results in json format.

        Returns:
            A tuple with the exit code and results json.
        """
        if self.provider == 'ssh':
            # SSH provider: instance must be running
            pass
        elif self.running_instance_id:
            # Use existing instance
            self._start_instance_if_stopped()
            self._set_image_id()
        else:
            # Launch new instance
            self.logger.info('Launching new instance')
            self._launch_instance()
            self.logger.debug('ID of instance: %s' % self.running_instance_id)

        if not self.instance_ip:
            self._set_instance_ip()
            self.logger.debug('IP of instance: %s' % self.instance_ip)

        try:
            # Ensure instance running and SSH connection
            # can be established prior to testing instance.
            client = self._get_ssh_client()
            self.host_key_fingerprint = ipa_utils.get_host_key_fingerprint(
                client
            )
        except IpaSSHException as error:
            raise IpaProviderException(
                'Unable to connect to instance: %s' % error
            )
        except Exception as error:
            raise IpaProviderException(
                'An error occurred retrieving host key: %s' % error
            )

        self._set_results_dir()
        self._set_distro()
        self._log_info()

        if self.inject:
            self.process_injection_file(self._get_ssh_client())

        status = 0
        with ipa_utils.ssh_config(self.ssh_user, self.ssh_private_key_file)\
                as ssh_config:
            for item in self.test_files:
                if item == 'test_hard_reboot' and self.provider != 'ssh':
                    self.logger.info('Testing hard reboot')
                    start = time.time()
                    result = 1

                    try:
                        self.hard_reboot_instance()
                        client = self._get_ssh_client()

                        if self.host_key_fingerprint != \
                                ipa_utils.get_host_key_fingerprint(client):
                            raise Exception('Host key has changed.')

                        result = 0
                    except IpaSSHException as error:
                        self.logger.error(
                            'Unable to connect to instance after '
                            'hard reboot: %s' % error
                        )
                        break
                    except Exception as error:
                        self.logger.error(
                            'Instance failed hard reboot: %s' % error
                        )
                        break
                    finally:
                        duration = time.time() - start
                        self._process_test_results(
                            duration, 'test_hard_reboot', result
                        )
                        status = status or result

                elif item == 'test_soft_reboot':
                    self.logger.info('Testing soft reboot')
                    start = time.time()
                    result = 1

                    try:
                        self.distro.reboot(self._get_ssh_client())
                        client = self._get_ssh_client()

                        if self.host_key_fingerprint != \
                                ipa_utils.get_host_key_fingerprint(client):
                            raise Exception('Host key has changed.')

                        result = 0
                    except IpaSSHException as error:
                        self.logger.error(
                            'Unable to connect to instance after '
                            'soft reboot: %s' % error
                        )
                        break
                    except Exception as error:
                        self.logger.error(
                            'Instance failed soft reboot: %s' % error
                        )
                        break
                    finally:
                        duration = time.time() - start
                        self._process_test_results(
                            duration, 'test_soft_reboot', result
                        )
                        status = status or result

                elif item == 'test_update':
                    self.logger.info('Testing update')
                    start = time.time()
                    result = 1

                    try:
                        out = self.distro.update(self._get_ssh_client())
                        result = 0
                    except Exception as error:
                        self.logger.error('Instance failed to update')
                        self.logger.debug(error)
                    else:
                        with open(self.log_file, 'a') as log_file:
                            log_file.write(out)
                    finally:
                        duration = time.time() - start
                        self._process_test_results(
                            duration, 'test_update', result
                        )
                        status = status or result

                elif isinstance(item, set):
                    self.logger.info('Running tests %s' % ' '.join(item))
                    with open(self.log_file, 'a') as log_file:
                        with ipa_utils.redirect_output(log_file):
                            # Run tests
                            result = self._run_tests(item, ssh_config)
                            status = status or result

                else:
                    self.logger.error(
                        'Invalid test item in list: %s' % item
                    )

                if status and self.early_exit:
                    break
        # flag set to collect VM info
        if self.collect_vm_info:
            self._collect_vm_info()
        # If tests pass and cleanup flag is none, or
        # cleanup flag is true, terminate instance.
        if status == 0 and self.cleanup is None or self.cleanup:
            self.logger.info(
                'Terminating instance %s' % self.running_instance_id
            )
            self._terminate_instance()

        self._save_results()
        self._update_history()

        # Return status and results json
        return status, self.results
