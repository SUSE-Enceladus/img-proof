import pytest
import re

def test_sles_ec2_csp_cli(host, get_release_value, is_sle_micro):
    version = get_release_value('VERSION')
    assert version

    if is_sle_micro():
        pytest.skip('Micro has product version instead of SLE version.')

    match = re.match(r'^(\d+)(?:[.-](?:SP)?(\d+))?$', version)
    assert match, f"Unexpected version format: {version}"

    major = int(match.group(1))

    if major < 16:
        pytest.skip('Pre-SLE 16.0 versions do not have CSP CLI.')

    aws_cmd = host.run('aws --version')
    assert aws_cmd.rc == 0, f"'aws --version' failed with code {aws_cmd.rc}"
    assert 'aws-cli' in aws_cmd.stdout, "'aws-cli' not found in aws version output"
    assert 'botocore' in aws_cmd.stdout, "'botocore' not found in aws version output"