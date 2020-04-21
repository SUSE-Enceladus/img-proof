# -*- coding: utf-8 -*-

"""img-proof CLI endpoints using click library."""

# Copyright (c) 2019 SUSE LLC. All rights reserved.
#
# This file is part of img-proof. img-proof provides an api and command line
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

import logging
import os
import sys
import tarfile
import tempfile

import click

from img_proof.ipa_constants import (
    IPA_HISTORY_FILE,
    SUPPORTED_DISTROS,
    SUPPORTED_CLOUDS
)
from img_proof import ipa_utils
from img_proof.ipa_constants import TEST_PATHS
from img_proof.ipa_controller import collect_tests, test_image
from img_proof.scripts.cli_utils import (
    archive_history_item,
    echo_log,
    echo_results,
    echo_results_file,
    echo_style,
    get_log_file_from_item,
    results_history
)


def print_license(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    click.echo('GPLv3+')
    ctx.exit()


@click.group()
@click.version_option()
@click.option(
    '--license',
    is_flag=True,
    callback=print_license,
    expose_value=False,
    is_eager=True,
    help='Show license information and exit.'
)
@click.option(
    '--no-color',
    is_flag=True,
    help='Remove ANSI color and styling from output.'
)
@click.pass_context
def main(context, no_color):
    """
    img-proof provides a Python API and cmd line utility for testing images.

    It can be used to test images in the Public Cloud (AWS, Azure, GCE, etc.).
    """
    if context.obj is None:
        context.obj = {}
    context.obj['no_color'] = no_color


@click.command(context_settings=dict(token_normalize_func=str.lower))
@click.option(
    '--accelerated-networking',
    is_flag=True,
    help='Enable accelerated networking in Azure instance network interface.'
)
@click.option(
    '--access-key-id',
    help='EC2 access key ID for login credentials.'
)
@click.option(
    '-a',
    '--account',
    help='Settings account to provide connection information.'
)
@click.option(
    '--cleanup/--no-cleanup',
    default=None,
    help='Terminate instance after tests. By default an instance will be '
         'deleted on success and left running if there is a test failure.'
)
@click.option(
    '-C',
    '--config',
    type=click.Path(exists=True),
    help='img_proof config file location. Default: ~/.config/img_proof/config'
)
@click.option(
    '-D',
    '--description',
    help='Short description for test run.'
)
@click.option(
    '-d',
    '--distro',
    type=click.Choice(SUPPORTED_DISTROS),
    help='The distribution of the image.'
)
@click.option(
    '--early-exit',
    is_flag=True,
    help='Terminate test suite on first failure.'
)
@click.option(
    '-h',
    '--history-log',
    type=click.Path(),
    help='img-proof history log file location. '
         'Default: ~/.config/img_proof/.history'
)
@click.option(
    '-i',
    '--image-id',
    help='The ID of the image used for instance.'
)
@click.option(
    '--image-project',
    help='The image project where the image exists. This is required if '
         'testing an image in a project different than the service account '
         'project.'
)
@click.option(
    '--inject',
    help='Path to an injection yaml config file.',
    type=click.Path(exists=True)
)
@click.option(
    '-t',
    '--instance-type',
    help='Instance type to use for launching machine.'
)
@click.option(
    '--ip-address',
    help='IP address for the test instance (only used by SSH cloud).'
)
@click.option(
    '--debug',
    'log_level',
    flag_value=logging.DEBUG,
    help='Display debug level logging to console.'
)
@click.option(
    '--verbose',
    'log_level',
    flag_value=logging.INFO,
    default=True,
    help='(Default) Display logging info to console.'
)
@click.option(
    '--quiet',
    'log_level',
    flag_value=logging.WARNING,
    help='Silence logging information on test run.'
)
@click.option(
    '--no-default-test-dirs',
    is_flag=True,
    default=False,
    help='Do not include default test directories in search for tests.'
)
@click.option(
    '--cloud-config',
    help='The cloud specific config file location.'
)
@click.option(
    '--region',
    help='Cloud region to test image.'
)
@click.option(
    '--results-dir',
    help='Directory to store test results and output.'
)
@click.option(
    '-R',
    '--running-instance-id',
    help='The ID or Name of running instance to test.'
)
@click.option(
    '--secret-access-key',
    help='EC2 secret access key for login credentials.'
)
@click.option(
    '--security-group-id',
    help='EC2 security group id to assign to instances VPC.'
)
@click.option(
    '--service-account-file',
    help='GCE service account file for login credentials.'
)
@click.option(
    '--ssh-key-name',
    help='Optional SSH private key-pair name for EC2.'
)
@click.option(
    '--ssh-private-key-file',
    type=click.Path(exists=True),
    help='SSH private key file for accessing instance.'
)
@click.option(
    '-u',
    '--ssh-user',
    help='SSH user for accessing instance.'
)
@click.option(
    '--subnet-id',
    help='Subnet to launch the new instance into.'
)
@click.option(
    '--test-dirs',
    help='Directories to search for tests.'
)
@click.option(
    '--timeout',
    help='The time to wait when establishing an SSH '
         'connection and for instances to change state.',
    type=click.IntRange(min=1)
)
@click.option(
    '--vnet-name',
    help='Azure virtual network name to attach network interface.'
)
@click.option(
    '--vnet-resource-group',
    help='Azure resource group name where virtual network is found.'
)
@click.option(
    '--collect-vm-info',
    is_flag=True,
    help='Controls whether general info about VM in cloud should be collected'
)
@click.argument(
    'cloud',
    type=click.Choice(SUPPORTED_CLOUDS)
)
@click.option(
    '--compartment-id',
    help='The OCI compartment to use for image testing.'
)
@click.option(
    '--availability-domain',
    help='The domain to place the instance and networking for testing.'
)
@click.option(
    '--signing-key-fingerprint',
    help='The public fingerprint of the OCI signing key.'
)
@click.option(
    '--signing-key-file',
    help='The OCI key file path used for API signing.'
)
@click.option(
    '--tenancy',
    help='The tenancy for the OCI user.'
)
@click.option(
    '--oci-user-id',
    help='The ID for the OCI user.'
)
@click.option(
    '--enable-secure-boot',
    is_flag=True,
    help='Enable secure boot for the instance. Secure boot requires '
         'UEFI boot firmware.'
)
@click.option(
    '--enable-uefi',
    is_flag=True,
    help='Enable boot firmware for the instance. By default secure boot '
         'is disabled.'
)
@click.argument('tests', nargs=-1)
@click.pass_context
def test(context,
         accelerated_networking,
         access_key_id,
         account,
         cleanup,
         config,
         description,
         distro,
         early_exit,
         history_log,
         image_id,
         image_project,
         inject,
         instance_type,
         ip_address,
         log_level,
         no_default_test_dirs,
         cloud_config,
         region,
         results_dir,
         running_instance_id,
         secret_access_key,
         security_group_id,
         service_account_file,
         ssh_key_name,
         ssh_private_key_file,
         ssh_user,
         subnet_id,
         test_dirs,
         timeout,
         vnet_name,
         vnet_resource_group,
         collect_vm_info,
         cloud,
         compartment_id,
         availability_domain,
         signing_key_fingerprint,
         signing_key_file,
         tenancy,
         oci_user_id,
         enable_secure_boot,
         enable_uefi,
         tests):
    """Test image in the given framework using the supplied test files."""
    no_color = context.obj['no_color']
    try:
        status, results = test_image(
            cloud,
            accelerated_networking,
            access_key_id,
            account,
            cleanup,
            config,
            description,
            distro,
            early_exit,
            history_log,
            image_id,
            image_project,
            inject,
            instance_type,
            ip_address,
            log_level,
            no_default_test_dirs,
            cloud_config,
            region,
            results_dir,
            running_instance_id,
            secret_access_key,
            security_group_id,
            service_account_file,
            ssh_key_name,
            ssh_private_key_file,
            ssh_user,
            subnet_id,
            test_dirs,
            tests,
            timeout,
            vnet_name,
            vnet_resource_group,
            collect_vm_info,
            compartment_id,
            availability_domain,
            signing_key_fingerprint,
            signing_key_file,
            tenancy,
            oci_user_id,
            enable_secure_boot,
            enable_uefi
        )
        echo_results(results, no_color)
        sys.exit(status)
    except Exception as error:
        if log_level == logging.DEBUG:
            raise

        echo_style(
            "{}: {}".format(type(error).__name__, error),
            no_color,
            fg='red'
        )
        sys.exit(1)


@click.group(invoke_without_command=True)
@click.option(
    '--history-log',
    default=IPA_HISTORY_FILE,
    type=click.Path(exists=True),
    help='Location of the history log file to display results from.'
)
@click.pass_context
def results(context, history_log):
    """Process provided history log and results files."""
    if context.obj is None:
        context.obj = {}
    context.obj['history_log'] = history_log

    if context.invoked_subcommand is None:
        context.invoke(show, item=1)


@click.command()
@click.option(
    '-c',
    '--clear-log',
    help='Clear the history log after archiving.',
    is_flag=True
)
@click.option(
    '-i',
    '--items',
    help='List of history items to archive. Must be a comma separated list.',
    type=click.STRING
)
@click.argument(
    'path',
    type=click.Path(exists=True),
)
@click.argument(
    'name',
    type=click.STRING
)
@click.pass_context
def archive(context, clear_log, items, path, name):
    """
    Archive the history log and all results/log files.

    After archive is created optionally clear the history log.
    """
    history_log = context.obj['history_log']
    no_color = context.obj['no_color']

    with open(history_log, 'r') as f:
        # Get history items
        history_items = f.readlines()

    if items:
        # Split comma separated list and cast indices to integer.
        items = [int(item) for item in items.split(',')]

        lines = []
        for index in items:
            lines.append(history_items[len(history_items) - index])
        history_items = lines

    with tempfile.TemporaryDirectory() as temp_dir:
        for item in history_items:
            # Copy log and results file,
            # update results file with relative path.
            archive_history_item(item, temp_dir, no_color)

        file_name = ''.join([name, '.tar.gz'])
        archive_path = os.path.join(path, file_name)

        with tarfile.open(archive_path, "w:gz") as tar:
            # Create tar archive
            tar.add(temp_dir, arcname='results')

    if clear_log:
        if items:
            # Remove duplicates to prevent unwanted deletion.
            items = list(set(items))

            # Must delete items from bottom to top of history file
            # to preserve indices. (Index 0 is last item in file)
            items.sort()
            for index in items:
                context.invoke(delete, item=index)
        else:
            context.invoke(clear)

    click.echo(
        'Exported results history to archive: {0}'.format(archive_path)
    )


@click.command()
@click.pass_context
def clear(context):
    """
    Clear the results from the history file.
    """
    ipa_utils.update_history_log(context.obj['history_log'], clear=True)


@click.command()
@click.argument(
    'item',
    type=click.INT
)
@click.pass_context
def delete(context, item):
    """
    Delete the specified history item from the history log.
    """
    history_log = context.obj['history_log']
    no_color = context.obj['no_color']
    try:
        with open(history_log, 'r+') as f:
            lines = f.readlines()
            history = lines.pop(len(lines) - item)
            f.seek(0)
            f.write(''.join(lines))
            f.flush()
            f.truncate()
    except IndexError:
        echo_style(
            'History result at index %s does not exist.' % item,
            no_color,
            fg='red'
        )
        sys.exit(1)
    except Exception as error:
        echo_style(
            'Unable to delete result item {0}. {1}'.format(item, error),
            no_color,
            fg='red'
        )
        sys.exit(1)

    log_file = get_log_file_from_item(history)
    try:
        os.remove(log_file)
    except Exception:
        echo_style(
            'Unable to delete results file for item {0}.'.format(item),
            no_color,
            fg='red'
        )

    try:
        os.remove(log_file.rsplit('.', 1)[0] + '.results')
    except Exception:
        echo_style(
            'Unable to delete log file for item {0}.'.format(item),
            no_color,
            fg='red'
        )


@click.command(name='list')
@click.pass_context
def list_results(context):
    """
    Display list of results history.
    """
    results_history(context.obj['history_log'], context.obj['no_color'])


@click.command()
@click.option(
    '-l',
    '--log',
    is_flag=True,
    help='Display the log for the given test run.'
)
@click.option(
    '-r',
    '--results-file',
    type=click.Path(exists=True),
    help='The results file or log to parse.'
)
@click.option(
    '-v',
    '--verbose',
    is_flag=True
)
@click.argument(
    'item',
    default=1
)
@click.pass_context
def show(context,
         log,
         results_file,
         verbose,
         item):
    """
    Print test results info from provided results json file.

    If no results file is supplied echo results from most recent
    test in history if it exists.

    If verbose option selected, echo all test cases.

    If log option selected echo test log.
    """
    history_log = context.obj['history_log']
    no_color = context.obj['no_color']
    if not results_file:
        # Find results/log file from history
        # Default -1 is most recent test run
        try:
            with open(history_log, 'r') as f:
                lines = f.readlines()
            history = lines[len(lines) - item]
        except IndexError:
            echo_style(
                'History result at index %s does not exist.' % item,
                no_color,
                fg='red'
            )
            sys.exit(1)
        except Exception:
            echo_style(
                'Unable to retrieve results history, '
                'provide results file or re-run test.',
                no_color,
                fg='red'
            )
            sys.exit(1)

        log_file = get_log_file_from_item(history)
        if log:
            echo_log(log_file, no_color)
        else:
            echo_results_file(
                log_file.rsplit('.', 1)[0] + '.results',
                no_color,
                verbose
            )

    elif log:
        # Log file provided
        log_file = results_file.rsplit('.', 1)[0] + '.log'
        echo_log(log_file, no_color)
    else:
        # Results file provided
        echo_results_file(results_file, no_color, verbose)


@click.command(name='list')
@click.option(
    '-v',
    '--verbose',
    is_flag=True
)
@click.argument(
    'test_dirs',
    nargs=-1,
    type=click.Path(exists=True)
)
@click.pass_context
def list_tests(context, verbose, test_dirs):
    """
    Print a list of test files or test cases.

    If verbose option selected, print all tests cases in
    each test file, otherwise print the test files only.

    If test_dirs supplied they will be used to search for
    tests otherwise the default test directories are used.
    """
    no_color = context.obj['no_color']
    test_dirs = test_dirs or TEST_PATHS

    try:
        results = collect_tests(test_dirs, verbose)
    except Exception as error:
        echo_style(
            "An error occurred retrieving test files: {}".format(error),
            no_color,
            fg='red'
        )
        sys.exit(1)

    if verbose:
        for index, test_file in enumerate(results):
            if index % 2 == 0:
                fg = 'blue'
            else:
                fg = 'green'

            echo_style(
                '\n'.join(test_file),
                no_color,
                fg=fg
            )
    else:
        click.echo('\n'.join(results))


main.add_command(list_tests)
results.add_command(archive)
results.add_command(clear)
results.add_command(delete)
results.add_command(list_results)
results.add_command(show)
main.add_command(results)
main.add_command(test)
