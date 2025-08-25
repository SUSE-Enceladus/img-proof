import pytest


def test_sles_gcp_csp_cli(host, is_sle_micro, get_version):
    version = get_version()

    if is_sle_micro():
        pytest.skip('Micro has product version instead of SLE version.')

    if version < 16.0:
        pytest.skip('Pre-SLE 16.0 versions do not have CSP CLI.')

    which_cmd = host.run('command -v gcloud')
    assert which_cmd.rc == 0, f"'{which_cmd.command}' failed with code {which_cmd.rc}."

    gcp_cmd = host.run('gcloud --version')
    assert gcp_cmd.rc == 0, f"'{gcp_cmd.command}' failed with code {gcp_cmd.rc}"
    assert 'Google Cloud SDK' in gcp_cmd.stdout, \
        "'Google Cloud SDK' not found in gcloud version output"
    assert 'core' in gcp_cmd.stdout, \
        "'core' not found in gcloud version output"
    assert 'minikube' in gcp_cmd.stdout, \
        "'minikube' not found in gcloud version output"
