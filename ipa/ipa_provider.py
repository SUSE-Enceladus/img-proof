# -*- coding: utf-8 -*-

"""Base provider class for testing cloud images."""

# Copyright (c) 2017 SUSE LLC
#
# This file is part of ipa.
#
# See LICENSE for license information.

import importlib
import json
import os
import shlex
from datetime import datetime

from ipa import ipa_utils
from ipa.ipa_constants import (
    IPA_CONFIG_FILE,
    IPA_RESULTS_PATH,
    NOT_IMPLEMENTED,
    SUPPORTED_DISTROS,
    TEST_PATHS
)
from ipa.ipa_exceptions import (
    IpaProviderException,
    IpaSSHException,
    IpaUtilsException
)
from ipa.results_plugin import JSONReport

import pytest


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
                 distro_name=None,
                 image_id=None,
                 instance_type=None,
                 region=None,
                 results_dir=None,
                 running_instance=None,
                 terminate=None,
                 test_dirs=None,
                 test_files=None):
        """Initialize base provider class."""
        super(IpaProvider, self).__init__()
        # Get ipa ini config file
        self.config = config or IPA_CONFIG_FILE
        self.ipa_config = ipa_utils.get_config(self.config)

        self.instance_ip = None
        self.provider = provider
        self.results = None

        self.cleanup = self._get_value(cleanup)
        self.distro_name = self._get_value(distro_name)
        self.image_id = self._get_value(image_id)
        self.instance_type = self._get_value(instance_type)
        self.running_instance = self._get_value(running_instance)
        self.terminate = self._get_value(terminate)
        self.test_files = list(self._get_value(test_files, default=[]))

        self.region = self._get_value(
            region,
            config_key='region'
        )

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

        if not self.image_id and not self.running_instance:
            raise IpaProviderException(
                'Image ID or running instance is required.'
            )

        if not self.test_files:
            raise IpaProviderException('No test files found.')

        self._parse_test_files(test_dirs)

    def _get_instance(self):
        raise NotImplementedError(NOT_IMPLEMENTED)

    def _get_instance_state(self):
        raise NotImplementedError(NOT_IMPLEMENTED)

    def _get_ssh_client(self):
        return ipa_utils.get_ssh_client(
            self.instance_ip,
            self.ssh_private_key,
            self.ssh_user
        )

    def _get_value(self, arg, config_key=None, default=None):
        """Return the correct value for the given arg."""
        value = default

        if arg or arg is False:
            value = arg

        elif config_key:
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

    def _merge_results(self, results):
        if self.results:
            self.results['tests'] += results['tests']

            for key, value in results['summary'].items():
                if key in self.results['summary']:
                    self.results['summary'][key] += results['summary'][key]
                else:
                    self.results['summary'][key] = results['summary'][key]
        else:
            self.results = results

    def _parse_test_files(self, test_dirs):
        """
        Collect all test dirs and expand test files.

        The test files are expanded to absolute paths given
        test names and a list of availble test dirs to use.
        """
        # TEST_PATHS is a tuple to be immutable.
        self.test_dirs = set(TEST_PATHS)
        if test_dirs:
            # Command line arg
            self.test_dirs.update(test_dirs)

        with ipa_utils.ignored(IpaUtilsException):
            # ipa config arg
            test_dirs = ipa_utils.get_from_config(
                self.ipa_config,
                self.provider,
                'ipa',
                'test_dirs'
            )

            if test_dirs:
                self.test_dirs.update(test_dirs.split(','))

        # Confirm all test dir paths are absolute and normalized
        # (remove redundant slashes .../ ...// etc.)
        self.test_dirs = set(
            os.path.normpath(
                os.path.expanduser(test_dir)
            ) for test_dir in self.test_dirs
        )

        self.test_files = ipa_utils.expand_test_files(
            self.test_dirs,
            self.test_files
        )

    def _run_tests(self, tests, ssh_config):
        """Run the test suite on the image."""
        options = []
        if self.terminate:
            options.append('-x')

        args = "-v {} --ssh-config={} --hosts={} {}".format(
            ' '.join(options),
            ssh_config,
            self.instance_ip,
            ' '.join(tests)
        )
        print(
            'Test directories: \n{}\n'.format(
                '\n'.join(self.test_dirs)
            )
        )
        print('Arguments: \n{}\n'.format(args))

        cmds = shlex.split(args)
        plugin = JSONReport()
        result = pytest.main(cmds, plugins=[plugin])
        self._merge_results(plugin.report)

        return result

    def _save_results(self):
        """Save results dictionary to json file."""
        with open(self.results_file, 'w') as results_file:
            json.dump(self.results, results_file)

    def _set_distro(self):
        """Determine distro for image and create instance of class."""
        if self.distro_name not in SUPPORTED_DISTROS:
            raise IpaProviderException(
                'Distribution: %s, not supported.' % self.distro_name
            )

        distro_module = importlib.import_module(
            'ipa.ipa_%s' % self.distro_name.lower()
        )
        self.distro = getattr(distro_module, self.distro_name)()

    def _set_image_id(self):
        raise NotImplementedError(NOT_IMPLEMENTED)

    def _set_instance_ip(self):
        raise NotImplementedError(NOT_IMPLEMENTED)

    def _set_results_dir(self):
        """Create results directory if not exists."""
        self.results_dir = os.path.join(
            self.results_dir,
            self.provider,
            self.image_id,
            self.running_instance
        )

        if not os.path.exists(self.results_dir):
            os.makedirs(self.results_dir)

        time_stamp = datetime.now().strftime('%Y%m%d%H%M%S')
        self.out_file = ''.join(
            [self.results_dir, os.sep, time_stamp, '.log']
        )

        self.results_file = ''.join(
            [self.results_dir, os.sep, time_stamp, '.results']
        )

    def _start_instance(self):
        """Start the instance."""
        raise NotImplementedError(NOT_IMPLEMENTED)

    def _start_instance_if_stopped(self):
        """Start instance if stopped."""
        if not self._is_instance_running():
            self._start_instance()

    def _stop_instance(self):
        """Stop the instance."""
        raise NotImplementedError(NOT_IMPLEMENTED)

    def _terminate_instance(self):
        """Terminate the instance."""
        raise NotImplementedError(NOT_IMPLEMENTED)

    def hard_reboot_instance(self):
        """Stop then start the instance."""
        self._stop_instance()
        self._start_instance()
        self._set_instance_ip()
        ipa_utils.clear_cache()

    def test_image(self):
        """
        The entry point for testing an image.

        Creates new or initiates existing instance. Runs
        test suite on instance. Collects and returns
        results in json format.

        Returns:
            A tuple with the exit code and results json.

        """
        if self.running_instance:
            # Use existing instance
            self._start_instance_if_stopped()
            self._set_image_id()
        else:
            # Launch new instance
            self._launch_instance()
        self._set_instance_ip()

        try:
            # Ensure instance running and SSH connection
            # can be established prior to testing instance.
            self._get_ssh_client()
        except IpaSSHException as error:
            raise IpaProviderException(
                'Unable to connect to instance: %s' % error
            )

        self._set_results_dir()
        self._set_distro()
        status = 0

        with ipa_utils.ssh_config(self.ssh_user, self.ssh_private_key)\
                as ssh_config:
            for item in self.test_files:
                if item == 'test_hard_reboot':
                    try:
                        self.hard_reboot_instance()
                        self._get_ssh_client()
                    except IpaSSHException as error:
                        raise IpaProviderException(
                            'Unable to connect to instance after '
                            'hard reboot: %s' % error
                        )
                    except Exception as error:
                        raise IpaProviderException(
                            'Instance failed hard reboot: %s' % error
                        )
                elif item == 'test_soft_reboot':
                    try:
                        self.distro.reboot(self._get_ssh_client())
                        self._get_ssh_client()
                    except IpaSSHException as error:
                        raise IpaProviderException(
                            'Unable to connect to instance after '
                            'soft reboot: %s' % error
                        )
                    except Exception as error:
                        raise IpaProviderException(
                            'Instance failed soft reboot: %s' % error
                        )
                elif isinstance(item, set):
                    with open(self.out_file, 'a') as out_file:
                        with ipa_utils.redirect_output(out_file):
                            # Run tests
                            status = (status or
                                      self._run_tests(item, ssh_config))
                else:
                    # Todo log unidentified test item and/or raise exception
                    pass

                if status and self.terminate:
                    break

        # If tests pass and cleanup flag is none, or
        # cleanup flag is true, terminate instance.
        if status == 0 and self.cleanup is None or self.cleanup:
            self._terminate_instance()

        self._save_results()

        # Return status and results json
        return status, self.results['summary']
