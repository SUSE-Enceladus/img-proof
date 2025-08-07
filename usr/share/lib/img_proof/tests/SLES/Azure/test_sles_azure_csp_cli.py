import pytest
import re

def test_sles_azure_csp_cli(host, get_release_value, is_sle_micro):
    version = get_release_value('VERSION')
    assert version

    if is_sle_micro():
        pytest.skip('Micro has product version instead of SLE version.')

    match = re.match(r'^(\d+)(?:[.-](?:SP)?(\d+))?$', version)
    assert match, f"Unexpected version format: {version}"

    major = match.group(1)
    patchlevel = match.group(2)

    if int(major) < 16:
        pytest.skip('Pre-SLE 16.0 versions do not have CSP CLI.')


    az_cmd = host.run('az --version')
    assert az_cmd.rc == 0, f"'az --version' failed with code {az_cmd.rc}"
    assert 'azure-cli' in az_cmd.stdout, "Missing expected 'azure-cli' in version output"
    assert 'core' in az_cmd.stdout, "Missing expected 'core' in version output"
    assert 'msal' in az_cmd.stdout, "Missing expected 'msal' in version output"
    assert 'azure-mgmt-resource' in az_cmd.stdout, "Missing expected 'azure-mgmt-resource' in version output"