import pytest


def test_sles_azure_csp_cli(
    host,
    is_sle_micro,
    is_suma,
    is_chost,
    get_version
):
    version = get_version()

    if is_sle_micro() or is_suma() or is_chost():
        pytest.skip('Skip image that does not contain the Azure CLI.')

    which_cmd = host.run('command -v az')
    assert which_cmd.rc == 0, \
        f"'{which_cmd.command}' failed with code {which_cmd.rc}."

    az_cmd = host.run('az --version')
    assert az_cmd.rc == 0, f"'{az_cmd.command}' failed with code {az_cmd.rc}"

    assert 'azure-cli' in az_cmd.stdout, \
        "Missing expected 'azure-cli' in version output"
    assert 'core' in az_cmd.stdout, \
        "Missing expected 'core' in version output"

    if version >= 15.0:
        assert 'msal' in az_cmd.stdout, \
            "Missing expected 'msal' in version output"
        assert 'azure-mgmt-resource' in az_cmd.stdout, \
            "Missing expected 'azure-mgmt-resource' in version output"
    else:
        assert 'telemetry' in az_cmd.stdout, \
            "Missing expected 'telemetry' in version output"
