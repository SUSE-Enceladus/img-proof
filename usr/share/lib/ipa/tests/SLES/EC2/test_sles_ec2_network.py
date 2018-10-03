import pytest


types = {
    'c5d.large': 15.0,
    'd2.xlarge': 15.0,
    'i3.8xlarge': 15.0,
    'i3.metal': 15.0,
    'm5.large': 15.0,
    'm5d.large': 15.0,
    'r5.24xlarge': 15.0,
    't3.small': 15.0
}


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

    url = 'https://suse-download-test-{0}.s3.amazonaws.com/' \
          'SLE-15-Installer-DVD-x86_64-GM-DVD2.iso'.format(
              region
          )

    dl_result = host.run(
        'curl -o /dev/null -skw "%{{time_total}} %{{size_download}}"'
        ' {0}'.format(url)
    )

    dl_time, size = dl_result.stdout.strip().split(' ')
    if size != '1214599168':
        raise Exception('Download failed!')

    if float(dl_time) > types[instance_type]:
        raise Exception('Download took too long!')
