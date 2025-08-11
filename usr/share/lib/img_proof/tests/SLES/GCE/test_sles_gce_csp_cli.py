import pytest

def test_sles_gcp_csp_cli(host, is_sle_16_or_higher):
    if not is_sle_16_or_higher():
        pytest.skip('Pre-SLE 16.0 versions do not have CSP CLI.')

    gcp_cmd = host.run('gcloud --version')
    assert gcp_cmd.rc == 0, f"'gcloud help' failed with code {gcp_cmd.rc}"
    assert 'Google Cloud SDK' in gcp_cmd.stdout, "'Google Cloud SDK' not found in gcloud version output"
    assert 'core' in gcp_cmd.stdout, "'core' not found in gcloud version output"
    assert 'minikube' in gcp_cmd.stdout, "'minikube' not found in gcloud version output"