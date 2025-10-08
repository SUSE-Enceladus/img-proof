import pytest
import re


@pytest.mark.skipinbeta
def test_sles_kernel_version(host, get_version, is_sle_micro):
    version = get_version()
    assert version

    if version <= 12.3 or version >= 16.0:
        pytest.skip(
            'Whoops! Image does not have distro version in kernel config.'
        )

    if is_sle_micro():
        pytest.skip('Micro has product version instead of SLE version.')

    match = re.match(r'^(\d+)(?:[.-](?:SP)?(\d+))?$', str(version))
    assert match, f"Unexpected version format: {str(version)}"

    major = match.group(1)
    patchlevel = match.group(2)

    config = host.run('sudo zcat /proc/config.gz')
    assert config.rc == 0, "Failed to read kernel config"

    assert f'CONFIG_SUSE_VERSION={major}\n' in config.stdout

    if patchlevel is not None:
        assert f'CONFIG_SUSE_PATCHLEVEL={patchlevel}\n' in config.stdout
