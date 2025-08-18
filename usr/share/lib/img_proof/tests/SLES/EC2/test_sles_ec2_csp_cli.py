import pytest


def test_sles_ec2_csp_cli(host, is_sle_micro, get_version):
    version = get_version()

    if is_sle_micro():
        pytest.skip('Micro has product version instead of SLE version.')

    if version < 16.0:
        pytest.skip('Pre-SLE 16.0 versions do not have CSP CLI.')

    aws_cmd = host.run('aws --version')
    assert aws_cmd.rc == 0, f"'aws --version' failed with code {aws_cmd.rc}"
    assert 'aws-cli' in aws_cmd.stdout, \
        "'aws-cli' not found in aws version output"
    assert 'botocore' in aws_cmd.stdout, \
        "'botocore' not found in aws version output"
