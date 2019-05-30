import pytest


types = (
    'c5d.large',
    'd2.xlarge',
    'i3.8xlarge',
    'i3.metal',
    'm5.large',
    'm5d.large',
    'r5.24xlarge',
    't3.small'
)

special_regions = [
    'ap-northeast-3',
    'cn-north-1',
    'cn-northwest-1',
    'us-gov-west-1'
]

dl_time = 15


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

    for i in range(3):
        dl_result = host.run(
            'curl -o /dev/null --max-time {0} --silent '
            '--write-out "%{{size_download}}|%{{http_code}}" {1}'.format(
                dl_time,
                url
            )
        )

        size, code = dl_result.stdout.strip().split('|')

        if code == '200' and size == '1214599168':
            return

    if code != '200':
        pytest.fail('Image ISO not found for region: {0}'.format(region))
    elif size != '1214599168':
        pytest.fail('Download failed. Size: {0}'.format(str(size)))
