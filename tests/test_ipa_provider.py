#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""Ipa provider unit tests."""

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

import io
import pytest
import os

from ipa import ipa_utils
from ipa.ipa_distro import Distro
from ipa.ipa_exceptions import IpaProviderException, IpaSSHException
from ipa.ipa_provider import IpaProvider

from unittest.mock import call, MagicMock, patch
from tempfile import TemporaryDirectory

args = ['ec2']

NOT_IMPL_METHODS = [
    '_get_instance',
    '_get_instance_state',
    '_is_instance_running',
    '_launch_instance',
    '_set_image_id',
    '_set_instance_ip',
    '_start_instance',
    '_stop_instance',
    '_terminate_instance'
]


class TestIpaProvider(object):
    """Ipa Provider test class."""

    @classmethod
    def setup_class(cls):
        """Set up temp results directory."""
        cls.results_dir = TemporaryDirectory()

    @classmethod
    def teardown_class(cls):
        """Cleanup results."""
        cls.results_dir.cleanup()

    def setup_method(self, method):
        """Set up kwargs dict."""
        self.kwargs = {
            'config': 'tests/data/config',
            'distro_name': 'SLES',
            'history_log': os.path.join(self.results_dir.name, '.history'),
            'image_id': 'fakeimage',
            'no_default_test_dirs': True,
            'results_dir': self.results_dir.name,
            'test_dirs': 'tests/data/tests',
            'test_files': ['test_image']
        }

    @pytest.mark.parametrize(
        "method",
        NOT_IMPL_METHODS,
        ids=NOT_IMPL_METHODS
    )
    def test_provider_not_implemented_methods(self, method):
        """Confirm methods raise not implemented exception."""
        provider = IpaProvider(*args, **self.kwargs)

        with pytest.raises(NotImplementedError) as error:
            getattr(provider, method)()
        assert str(error.value) == 'Implement method in child classes.'

    def test_provider_distro_required(self):
        """Test exception raised if no distro provided."""
        with pytest.raises(IpaProviderException) as error:
            IpaProvider(*args, config='tests/data/config')

        assert str(error.value) == \
            'Distro name is required.'

    def test_provider_instance_image_required(self):
        """Test exception if no running instance or image id provided."""
        with pytest.raises(IpaProviderException) as error:
            IpaProvider(
                *args,
                config='tests/data/config',
                distro_name='SLES'
            )

        assert str(error.value) == \
            'Image ID or running instance is required.'

    @patch.object(ipa_utils, 'get_ssh_client')
    def test_provider_get_ssh_client(self, mock_get_ssh_client):
        """Test get ssh client method."""
        provider = IpaProvider(*args, **self.kwargs)

        provider.instance_ip = '127.0.0.1'
        provider.ssh_user = 'ec2-user'
        provider.ssh_private_key_file = 'tests/data/ida_test'

        client = MagicMock()
        mock_get_ssh_client.return_value = client

        val = provider._get_ssh_client()
        assert val == client
        assert mock_get_ssh_client.call_count == 1

        ipa_utils.clear_cache()

    def test_provider_get_non_null_values(self):
        """Test provider get non null values method."""
        provider = IpaProvider(*args, **self.kwargs)

        data = {'region': 'us-east-1', 'type': None}

        # Assert arg takes precedence
        val = provider._get_non_null_values(data)
        assert 'type' not in val
        assert val['region'] == 'us-east-1'

    def test_provider_merge_results(self):
        """Test merge results output."""
        provider = IpaProvider(*args, **self.kwargs)

        results = {
            "tests": [
                {"name": "ipa/tests/test_sles.py::test_sles",
                 "teardown": {"duration": 4.792213439941406e-05,
                              "outcome": "passed",
                              "name": "teardown"},
                 "setup": {"duration": 9.799003601074219e-05,
                           "outcome": "passed",
                           "name": "setup"},
                 "run_index": 0,
                 "call": {"duration": 6.4849853515625e-05,
                          "outcome": "passed",
                          "name": "call"},
                 "duration": 0.00030875205993652344,
                 "outcome": "passed"}
            ],
            "summary": {"duration": 0.004277944564819336,
                        "passed": 1,
                        "num_tests": 1,
                        "failed": 0}
        }

        provider._merge_results(results)
        for key, val in results['summary'].items():
            assert provider.results['summary'][key] == val

        for key, val in results['tests'][0].items():
            assert provider.results['tests'][0][key] == val

    def test_process_test_results(self):
        provider = IpaProvider(*args, **self.kwargs)
        provider._process_test_results(5.0, 'test_test')

        assert provider.results['summary']['duration'] == 5.0
        assert provider.results['summary']['num_tests'] == 1
        assert provider.results['summary']['passed'] == 1

        test = provider.results['tests'][0]
        assert test['outcome'] == 'passed'
        assert test['name'] == 'test_test'

    @patch.object(IpaProvider, '_merge_results')
    @patch.object(pytest, 'main')
    def test_provider_run_tests(self, mock_pytest, mock_merge_results):
        """Test run tests method."""
        mock_pytest.return_value = 0
        mock_merge_results.return_value = None

        provider = IpaProvider(*args, **self.kwargs)

        provider.terminate = True
        provider.results['info'] = {
            'platform': 'ec2',
            'region': 'us-west-1'
        }

        out = provider._run_tests(
            ['tests/data/tests/test_image.py'],
            'test.ssh'
        )
        assert out == 0
        assert mock_pytest.call_count == 1
        assert mock_merge_results.call_count == 1

    def test_provider_invalid_distro_name(self):
        """Test invalid distro name provided raises exception."""
        provider = IpaProvider(*args, **self.kwargs)
        provider.distro_name = 'BadDistro'

        with pytest.raises(IpaProviderException) as error:
            provider._set_distro()
        assert str(error.value) == 'Distribution: BadDistro, not supported.'

    @patch.object(IpaProvider, '_is_instance_running')
    @patch.object(IpaProvider, '_start_instance')
    def test_provider_start_if_stopped(self,
                                       mock_start_instance,
                                       mock_instance_running):
        """Test start instance if stopped method."""
        mock_instance_running.return_value = False
        mock_start_instance.return_value = None

        provider = IpaProvider(*args, **self.kwargs)
        provider._start_instance_if_stopped()

        assert mock_instance_running.call_count == 1
        assert mock_start_instance.call_count == 1

    @patch('ipa.ipa_utils.execute_ssh_command')
    def test_provider_execute_ssh_command(self, mock_exec_cmd):
        client = MagicMock()
        mock_exec_cmd.return_value = 'command executed successfully!'

        provider = IpaProvider(*args, **self.kwargs)
        provider.log_file = 'fake_file.name'

        with patch('builtins.open', create=True) as mock_open:
            mock_open.return_value = MagicMock(spec=io.IOBase)
            file_handle = mock_open.return_value.__enter__.return_value

            provider.execute_ssh_command(client, 'python test.py')

            file_handle.write.assert_has_calls([
                call('\n'),
                call('command executed successfully!')
            ])

    @patch('ipa.ipa_utils.extract_archive')
    def test_provider_extract_archive(self, mock_extract_archive):
        client = MagicMock()

        mock_extract_archive.return_value = 'archive extracted successfully!'

        provider = IpaProvider(*args, **self.kwargs)
        provider.log_file = 'fake_file.name'

        with patch('builtins.open', create=True) as mock_open:
            mock_open.return_value = MagicMock(spec=io.IOBase)
            file_handle = mock_open.return_value.__enter__.return_value

            provider.extract_archive(client, 'archive.tar.xz')

            file_handle.write.assert_has_calls([
                call('\n'),
                call('archive extracted successfully!')
            ])

        mock_extract_archive.assert_called_once_with(
            client, 'archive.tar.xz', None
        )

    @patch.object(IpaProvider, '_set_instance_ip')
    @patch.object(IpaProvider, '_stop_instance')
    @patch.object(IpaProvider, '_start_instance')
    def test_provider_hard_reboot(self,
                                  mock_start_instance,
                                  mock_stop_instance,
                                  mock_set_instance_ip):
        """Test start instance if stopped method."""
        mock_stop_instance.return_value = None
        mock_start_instance.return_value = None
        mock_set_instance_ip.return_value = None

        provider = IpaProvider(*args, **self.kwargs)
        provider.instance_ip = '0.0.0.0'
        provider.hard_reboot_instance()

        assert mock_stop_instance.call_count == 1
        assert mock_start_instance.call_count == 1
        assert mock_set_instance_ip.call_count == 1

    @patch('ipa.ipa_utils.put_file')
    def test_provider_put_file(self, mock_put_file):
        client = MagicMock()

        file_path = '/home/user/test.file'
        basename = 'test.file'

        provider = IpaProvider(*args, **self.kwargs)
        out = provider.put_file(client, file_path)

        assert out == basename

        mock_put_file.assert_called_once_with(
            client, file_path, basename
        )

    def test_provider_install_package(self):
        client = MagicMock()
        distro = MagicMock()
        distro.install_package.return_value = 'package install successful!'

        provider = IpaProvider(*args, **self.kwargs)
        provider.log_file = 'fake_file.name'
        provider.distro = distro

        with patch('builtins.open', create=True) as mock_open:
            mock_open.return_value = MagicMock(spec=io.IOBase)
            file_handle = mock_open.return_value.__enter__.return_value

            provider.install_package(client, 'python')

            file_handle.write.assert_has_calls([
                call('\n'),
                call('package install successful!')
            ])

    @patch.object(IpaProvider, 'execute_ssh_command')
    @patch.object(IpaProvider, 'extract_archive')
    @patch.object(IpaProvider, 'install_package')
    @patch.object(IpaProvider, 'put_file')
    def test_process_injection_file(self,
                                    mock_put_file,
                                    mock_install_package,
                                    mock_extract_archive,
                                    mock_execute_command):
        client = MagicMock()
        mock_put_file.side_effect = [
            'test.noarch.rpm', 'test.tar.xz', 'test.py'
        ]

        provider = IpaProvider(*args, **self.kwargs)
        provider.inject = 'tests/data/injection/test_injection.yaml'

        provider.process_injection_file(client)

        mock_put_file.assert_has_calls([
            call(client, '/home/user/test.noarch.rpm'),
            call(client, '/home/user/test.tar.xz'),
            call(client, '/home/user/test.py')
        ])

        mock_install_package.assert_has_calls([
            call(client, 'test.noarch.rpm'),
            call(client, 'python3')
        ])

        mock_extract_archive.assert_called_once_with(
            client, 'test.tar.xz'
        )

        mock_execute_command.assert_called_once_with(
            client, 'python test.py'
        )

    @patch.object(IpaProvider, '_set_instance_ip')
    @patch.object(IpaProvider, '_set_image_id')
    @patch.object(IpaProvider, '_start_instance_if_stopped')
    @patch.object(IpaProvider, '_get_ssh_client')
    def test_provider_unable_connect_instance(self,
                                              mock_get_ssh_client,
                                              mock_start_instance,
                                              mock_set_image_id,
                                              mock_set_instance_ip):
        """Test exception raised when connection cannot be established."""
        mock_get_ssh_client.side_effect = IpaSSHException('ERROR!')
        mock_start_instance.return_value = None
        mock_set_image_id.return_value = None
        mock_set_instance_ip.return_value = None
        self.kwargs['running_instance_id'] = 'fakeinstance'

        provider = IpaProvider(*args, **self.kwargs)
        with pytest.raises(IpaProviderException) as error:
            provider.test_image()
        assert str(error.value) == 'Unable to connect to instance: ERROR!'
        assert mock_get_ssh_client.call_count == 1

    @patch.object(IpaProvider, '_set_instance_ip')
    @patch.object(IpaProvider, '_set_image_id')
    @patch.object(IpaProvider, '_start_instance_if_stopped')
    @patch.object(IpaProvider, '_get_ssh_client')
    @patch('ipa.ipa_utils.get_host_key_fingerprint')
    @patch.object(IpaProvider, 'hard_reboot_instance')
    def test_provider_bad_connect_hard_reboot(self,
                                              mock_hard_reboot,
                                              mock_get_host_key,
                                              mock_get_ssh_client,
                                              mock_start_instance,
                                              mock_set_image_id,
                                              mock_set_instance_ip):
        """Test exception when connection not established after hard reboot."""
        mock_hard_reboot.return_value = None
        mock_get_host_key.return_value = b'04820482'
        mock_get_ssh_client.side_effect = [None, IpaSSHException('ERROR!')]
        mock_start_instance.return_value = None
        mock_set_image_id.return_value = None
        mock_set_instance_ip.return_value = None
        self.kwargs['running_instance_id'] = 'fakeinstance'
        self.kwargs['test_files'] = ['test_hard_reboot']

        provider = IpaProvider(*args, **self.kwargs)
        provider.ssh_private_key_file = 'tests/data/ida_test'
        provider.ssh_user = 'root'
        provider.logger = MagicMock()

        provider.test_image()
        provider.logger.error.assert_called_once_with(
            'Unable to connect to instance after hard reboot: ERROR!'
        )
        provider.logger.error.reset_mock()

        assert mock_get_ssh_client.call_count > 0
        assert mock_hard_reboot.call_count == 1

        mock_hard_reboot.reset_mock()
        provider.results_dir = self.results_dir.name

        mock_get_ssh_client.side_effect = [None, Exception('ERROR!')]

        provider.test_image()
        provider.logger.error.assert_called_once_with(
            'Instance failed hard reboot: ERROR!'
        )

        assert mock_get_ssh_client.call_count > 0
        assert mock_hard_reboot.call_count == 1
        mock_hard_reboot.reset_mock()

    @patch.object(IpaProvider, '_set_instance_ip')
    @patch.object(IpaProvider, '_set_image_id')
    @patch.object(IpaProvider, '_start_instance_if_stopped')
    @patch.object(IpaProvider, '_get_ssh_client')
    @patch('ipa.ipa_utils.get_host_key_fingerprint')
    @patch.object(Distro, 'reboot')
    def test_provider_bad_connect_soft_reboot(self,
                                              mock_soft_reboot,
                                              mock_get_host_key,
                                              mock_get_ssh_client,
                                              mock_start_instance,
                                              mock_set_image_id,
                                              mock_set_instance_ip):
        """Test exception when connection not established after hard reboot."""
        mock_soft_reboot.return_value = None
        mock_get_host_key.return_value = b'04820482'
        mock_get_ssh_client.side_effect = [
            None,
            None,
            IpaSSHException('ERROR!')
        ]
        mock_start_instance.return_value = None
        mock_set_image_id.return_value = None
        mock_set_instance_ip.return_value = None
        self.kwargs['running_instance_id'] = 'fakeinstance'
        self.kwargs['test_files'] = ['test_soft_reboot']

        provider = IpaProvider(*args, **self.kwargs)
        provider.ssh_private_key_file = 'tests/data/ida_test'
        provider.ssh_user = 'root'
        provider.logger = MagicMock()

        provider.test_image()
        provider.logger.error.assert_called_once_with(
            'Unable to connect to instance after soft reboot: ERROR!'
        )
        provider.logger.error.reset_mock()

        assert mock_get_ssh_client.call_count > 0
        assert mock_soft_reboot.call_count == 1

        mock_soft_reboot.reset_mock()
        provider.results_dir = self.results_dir.name

        mock_get_ssh_client.side_effect = [None, None, Exception('ERROR!')]

        provider.test_image()
        provider.logger.error.assert_called_once_with(
            'Instance failed soft reboot: ERROR!'
        )

        assert mock_get_ssh_client.call_count > 0
        assert mock_soft_reboot.call_count == 1
        mock_soft_reboot.reset_mock()

    @patch.object(IpaProvider, '_set_instance_ip')
    @patch.object(IpaProvider, '_set_image_id')
    @patch.object(IpaProvider, '_start_instance_if_stopped')
    @patch.object(IpaProvider, '_get_ssh_client')
    @patch.object(IpaProvider, '_terminate_instance')
    @patch('ipa.ipa_utils.get_host_key_fingerprint')
    @patch.object(Distro, 'update')
    def test_provider_distro_update(self,
                                    mock_distro_update,
                                    mock_get_host_key,
                                    mock_terminate_instance,
                                    mock_get_ssh_client,
                                    mock_start_instance,
                                    mock_set_image_id,
                                    mock_set_instance_ip):
        """Test exception raised when invalid test item provided."""
        mock_distro_update.return_value = 'Updated!'
        mock_get_host_key.return_value = b'04820482'
        mock_terminate_instance.return_value = None
        mock_get_ssh_client.return_value = None
        mock_start_instance.return_value = None
        mock_set_image_id.return_value = None
        mock_set_instance_ip.return_value = None
        self.kwargs['running_instance_id'] = 'fakeinstance'
        self.kwargs['test_files'] = ['test_update']
        self.kwargs['cleanup'] = True

        provider = IpaProvider(*args, **self.kwargs)
        provider.ssh_private_key_file = 'tests/data/ida_test'
        provider.ssh_user = 'root'

        status, results = provider.test_image()
        assert status == 0
        assert mock_distro_update.call_count == 1
        self.kwargs['cleanup'] = None

    @patch.object(IpaProvider, '_set_instance_ip')
    @patch.object(IpaProvider, '_set_image_id')
    @patch.object(IpaProvider, '_start_instance_if_stopped')
    @patch.object(IpaProvider, '_get_ssh_client')
    @patch('ipa.ipa_utils.get_host_key_fingerprint')
    @patch.object(IpaProvider, '_run_tests')
    def test_provider_break_if_test_failure(self,
                                            mock_run_tests,
                                            mock_get_host_key,
                                            mock_get_ssh_client,
                                            mock_start_instance,
                                            mock_set_image_id,
                                            mock_set_instance_ip):
        """Test exception raised when invalid test item provided."""
        mock_run_tests.return_value = 1
        mock_get_host_key.return_value = b'04820482'
        mock_get_ssh_client.return_value = None
        mock_start_instance.return_value = None
        mock_set_image_id.return_value = None
        mock_set_instance_ip.return_value = None
        self.kwargs['running_instance_id'] = 'fakeinstance'
        self.kwargs['early_exit'] = True

        provider = IpaProvider(*args, **self.kwargs)
        provider.ssh_private_key_file = 'tests/data/ida_test'
        provider.ssh_user = 'root'

        status, results = provider.test_image()
        assert status == 1
        assert mock_run_tests.call_count == 1

    @patch.object(IpaProvider, '_get_instance_state')
    @patch('time.sleep')
    def test_azure_wait_on_instance(self,
                                    mock_sleep,
                                    mock_get_instance_state):
        """Test wait on instance method."""
        mock_get_instance_state.return_value = 'Stopped'
        mock_sleep.return_value = None

        provider = IpaProvider(*args, **self.kwargs)
        provider._wait_on_instance('Stopped')
        assert mock_get_instance_state.call_count == 1

    @patch.object(IpaProvider, '_get_ssh_client')
    def test_collect_vm_info(self, mock_get_ssh_client):
        """Test collect_vm_info method. """
        distro = MagicMock()
        client = MagicMock()
        distro.get_vm_info.return_value = \
            'Failed to collect VM info: Does not exist.'
        mock_get_ssh_client.return_value = client

        provider = IpaProvider(*args, **self.kwargs)
        provider.distro = distro
        provider.log_file = 'fake_file.name'
        provider.logger = MagicMock()

        with patch('builtins.open', create=True) as mock_open:
            mock_open.return_value = MagicMock(spec=io.IOBase)
            file_handle = mock_open.return_value.__enter__.return_value

            provider._collect_vm_info()

            file_handle.write.assert_has_calls([
                call('\n'),
                call('Failed to collect VM info: Does not exist.')
            ])

        provider.logger.info.assert_called_once_with(
            'Collecting basic info about VM'
        )
        assert mock_get_ssh_client.call_count == 1
