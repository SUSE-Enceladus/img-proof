import pytest

def test_sles_azure_csp_cli(host, is_sle_16_or_higher):
    if not is_sle_16_or_higher():
        pytest.skip('Pre-SLE 16.0 versions do not have CSP CLI.')

    az_cmd = host.run('az --version')
    assert az_cmd.rc == 0, f"'az --version' failed with code {az_cmd.rc}"
    assert 'azure-cli' in az_cmd.stdout, "Missing expected 'azure-cli' in version output"
    assert 'core' in az_cmd.stdout, "Missing expected 'core' in version output"
    assert 'msal' in az_cmd.stdout, "Missing expected 'msal' in version output"
    assert 'azure-mgmt-resource' in az_cmd.stdout, "Missing expected 'azure-mgmt-resource' in version output"