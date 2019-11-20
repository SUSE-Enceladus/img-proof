import pytest


def test_sles_kernel_version(host, get_release_value):
    version = get_release_value('VERSION')
    assert version

    if version in ('11.4', '12-SP1', '12-SP2', '12-SP3'):
        pytest.skip('Whoops! Image does not have version in kernel config.')

    version = version.split('-SP')
    config = host.run('sudo zcat /proc/config.gz')

    assert 'CONFIG_SUSE_VERSION={}\n'.format(version[0]) in config.stdout

    if len(version) > 1:
        assert 'CONFIG_SUSE_PATCHLEVEL={}\n'.format(
            version[1]
        ) in config.stdout
