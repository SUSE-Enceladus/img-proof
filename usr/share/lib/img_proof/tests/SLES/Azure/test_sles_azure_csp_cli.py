import pytest


def test_sles_azure_csp_cli(host, is_sle_micro, get_version):
    version = get_version()

    if is_sle_micro():
        pytest.skip('Micro has product version instead of SLE version.')

    if version < 16.0:
        pytest.skip('Pre-SLE 16.0 versions do not have CSP CLI.')

    which_cmd = host.run('command -v az')
    assert which_cmd.rc == 0, f"'{which_cmd.command}' failed with code {which_cmd.rc}."

    az_cmd = host.run('az --version')
    assert az_cmd.rc == 0, f"'{az_cmd.command}' failed with code {az_cmd.rc}"
    assert 'azure-cli' in az_cmd.stdout, \
        "Missing expected 'azure-cli' in version output"
    assert 'core' in az_cmd.stdout, "Missing expected 'core' in version output"
    assert 'msal' in az_cmd.stdout, "Missing expected 'msal' in version output"
    assert 'azure-mgmt-resource' in az_cmd.stdout, \
        "Missing expected 'azure-mgmt-resource' in version output"
