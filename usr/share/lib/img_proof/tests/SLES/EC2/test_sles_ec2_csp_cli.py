import pytest


def test_sles_ec2_csp_cli(host, is_sle_micro, is_suma, is_chost, get_version):
    version = get_version()

    if is_sle_micro() or is_suma() or is_chost():
        pytest.skip('Skip image that does not contain the AWS CLI.')

    which_cmd = host.run('command -v aws')
    assert which_cmd.rc == 0, \
        f"'{which_cmd.command}' failed with code {which_cmd.rc}."

    aws_cmd = host.run('aws --version')
    assert aws_cmd.rc == 0, \
        f"'{aws_cmd.command}' failed with code {aws_cmd.rc}"

    if version >= 15.0:
        assert 'aws-cli' in aws_cmd.stdout, \
            "'aws-cli' not found in aws version output"
        assert 'botocore' in aws_cmd.stdout, \
            "'botocore' not found in aws version output"
    else:
        # The python version in 12-sp5 dumps the output
        # to stderr even with exit code of 0
        assert 'aws-cli' in aws_cmd.stderr, \
            "'aws-cli' not found in aws version output"
        assert 'botocore' in aws_cmd.stderr, \
            "'botocore' not found in aws version output"
