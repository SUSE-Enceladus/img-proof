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

import pytest

from ipa import ipa_utils
from ipa.ipa_distro import Distro
from ipa.ipa_exceptions import IpaProviderException, IpaSSHException
from ipa.ipa_provider import IpaProvider

from unittest.mock import MagicMock, patch

args = ['EC2']

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

    def setup_method(self, method):
        """Set up kwargs dict."""
        self.kwargs = {
            'config': 'tests/data/config',
            'distro_name': 'SLES',
            'history_log': 'tests/data/results/.history',
            'image_id': 'fakeimage',
            'results_dir': 'tests/data/results',
            'test_dirs': ['tests/data/tests'],
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

    def test_provider_tests_required(self):
        """Test exception raised if no tests provided."""
        with pytest.raises(IpaProviderException) as error:
            IpaProvider(
                *args,
                config='tests/data/config',
                distro_name='SLES',
                image_id='test'
            )

        assert str(error.value) == 'No test files found.'

    @patch.object(ipa_utils, 'get_ssh_client')
    def test_provider_get_ssh_client(self, mock_get_ssh_client):
        """Test get ssh client method."""
        provider = IpaProvider(*args, **self.kwargs)

        provider.instance_ip = '127.0.0.1'
        provider.ssh_user = 'ec2-user'
        provider.ssh_private_key = 'tests/data/ida_test'

        client = MagicMock()
        mock_get_ssh_client.return_value = client

        val = provider._get_ssh_client()
        assert val == client
        assert mock_get_ssh_client.call_count == 1

        ipa_utils.clear_cache()

    def test_provider_get_value(self):
        """Test provider get value method."""
        provider = IpaProvider(*args, **self.kwargs)
        # Assert arg takes precedence
        val = provider._get_value(
            'us-east-1',
            config_key='region',
            default='us-east-2'
        )
        assert val == 'us-east-1'

        # With no arg default value is returned
        val = provider._get_value(None, default='us-east-2')
        assert val == 'us-east-2'

        # No arg and config value exists, config value returned
        val = provider._get_value(
            None,
            config_key='region',
            default='us-east-2'
        )
        assert val == 'us-west-1'

        # Assert default of none if no arg, config value or default supplied
        provider.ipa_config = ipa_utils.get_config(
            'tests/data/config.noregion'
        )
        val = provider._get_value(None, config_key='region')
        assert val is None

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

    def test_provider_string_test_files(self):
        """Test provider raises if test files is not a list, set or tuple."""
        self.kwargs['test_dirs'] = 'test/string/'

        with pytest.raises(IpaProviderException) as error:
            IpaProvider(*args, **self.kwargs)

        assert str(error.value) == \
            'Test dirs must be a list containing test directories.'

    @patch.object(IpaProvider, '_merge_results')
    @patch.object(pytest, 'main')
    def test_provider_run_tests(self, mock_pytest, mock_merge_results):
        """Test run tests method."""
        mock_pytest.return_value = 0
        mock_merge_results.return_value = None

        provider = IpaProvider(*args, **self.kwargs)

        provider.terminate = True
        provider.results['info'] = {
            'platform': 'EC2',
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
        provider.ssh_private_key = 'tests/data/ida_test'
        provider.ssh_user = 'root'

        with pytest.raises(IpaProviderException) as error:
            provider.test_image()
        assert str(error.value) == \
            'Unable to connect to instance after hard reboot: ERROR!'

        assert mock_get_ssh_client.call_count > 0
        assert mock_hard_reboot.call_count == 1
        mock_hard_reboot.reset_mock()

        mock_get_ssh_client.side_effect = [None, Exception('ERROR!')]
        with pytest.raises(IpaProviderException) as error:
            provider.test_image()
        assert str(error.value) == \
            'Instance failed hard reboot: ERROR!'

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
        provider.ssh_private_key = 'tests/data/ida_test'
        provider.ssh_user = 'root'

        with pytest.raises(IpaProviderException) as error:
            provider.test_image()
        assert str(error.value) == \
            'Unable to connect to instance after soft reboot: ERROR!'

        assert mock_get_ssh_client.call_count > 0
        assert mock_soft_reboot.call_count == 1
        mock_soft_reboot.reset_mock()

        mock_get_ssh_client.side_effect = [None, None, Exception('ERROR!')]
        with pytest.raises(IpaProviderException) as error:
            provider.test_image()
        assert str(error.value) == \
            'Instance failed soft reboot: ERROR!'

        assert mock_get_ssh_client.call_count > 0
        assert mock_soft_reboot.call_count == 1
        mock_soft_reboot.reset_mock()

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
        provider.ssh_private_key = 'tests/data/ida_test'
        provider.ssh_user = 'root'

        status, results = provider.test_image()
        assert status == 1
        assert mock_run_tests.call_count == 1
