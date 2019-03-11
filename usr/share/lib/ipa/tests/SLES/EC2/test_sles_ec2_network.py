import pytest


types = {
    'c5d.large': 15,
    'd2.xlarge': 15,
    'i3.8xlarge': 15,
    'i3.metal': 15,
    'm5.large': 15,
    'm5d.large': 15,
    'r5.24xlarge': 15,
    't3.small': 15
}

special_regions = [
    'ap-northeast-3',
    'cn-north-1',
    'cn-northwest-1',
    'us-gov-west-1'
]


def test_sles_ec2_network(determine_region, host):
    """
    Requires an S3 bucket in each region with the following name:
        suse-download-test-{region}

    Each bucket contains the iso:
        SLE-15-Installer-DVD-x86_64-GM-DVD2.iso
    """
    result = host.run(
        'curl http://169.254.169.254/latest/meta-data/instance-type'
    )
    instance_type = result.stdout.strip()

    if instance_type not in types:
        pytest.skip(
            'Unsupported EC2 instance type: {0}.'.format(instance_type)
        )

    region = determine_region('ec2')

    if region in special_regions:
        pytest.skip(
            'Skipped special region: {0}'.format(region)
        )

    url = 'https://suse-download-test-{0}.s3.amazonaws.com/' \
          'SLE-15-Installer-DVD-x86_64-GM-DVD2.iso'.format(
              region
          )

    dl_result = host.run(
        'curl -o /dev/null --max-time {0} --silent '
        '--write-out "%{{size_download}}|%{{http_code}}" {1}'.format(
            types[instance_type], url
        )
    )

    size, code = dl_result.stdout.strip().split('|')

    if code != '200':
        pytest.fail('Image ISO not found for region: {0}'.format(region))
    elif size != '1214599168':
        pytest.fail('Download failed. Size: {0}'.format(str(size)))
