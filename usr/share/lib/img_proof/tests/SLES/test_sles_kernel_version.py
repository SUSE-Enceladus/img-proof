import pytest
import re


def test_sles_kernel_version(host, get_release_value, is_sle_micro):
    version = get_release_value('VERSION')
    assert version

    if version in ('11.4', '12-SP1', '12-SP2', '12-SP3'):
        pytest.skip('Whoops! Image does not have version in kernel config.')

    if is_sle_micro():
        pytest.skip('Micro has product version instead of SLE version.')

    match = re.match(r'^(\d+)(?:[.-](?:SP)?(\d+))?$', version)
    assert match, f"Unexpected version format: {version}"

    major = match.group(1)
    patchlevel = match.group(2)

    config = host.run('sudo zcat /proc/config.gz')
    assert config.rc == 0, "Failed to read kernel config"

    assert f'CONFIG_SUSE_VERSION={major}\n' in config.stdout

    if patchlevel is not None:
        assert f'CONFIG_SUSE_PATCHLEVEL={patchlevel}\n' in config.stdout
