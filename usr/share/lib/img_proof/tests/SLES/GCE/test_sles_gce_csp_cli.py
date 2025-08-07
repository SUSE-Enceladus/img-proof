import pytest
import re

def test_sles_gcp_csp_cli(host, get_release_value, is_sle_micro):
    version = get_release_value('VERSION')
    assert version

    if is_sle_micro():
        pytest.skip('Micro has product version instead of SLE version.')

    match = re.match(r'^(\d+)(?:[.-](?:SP)?(\d+))?$', version)
    assert match, f"Unexpected version format: {version}"

    major = int(match.group(1))

    if major < 16:
        pytest.skip('Pre-SLE 16.0 versions do not have CSP CLI.')

    gcp_cmd = host.run('gcloud --version')
    assert gcp_cmd.rc == 0, f"'gcloud help' failed with code {gcp_cmd.rc}"
    assert 'Google Cloud SDK' in gcp_cmd.stdout, "'Google Cloud SDK' not found in gcloud version output"
    assert 'core' in gcp_cmd.stdout, "'core' not found in gcloud version output"
    assert 'minikube' in gcp_cmd.stdout, "'minikube' not found in gcloud version output"