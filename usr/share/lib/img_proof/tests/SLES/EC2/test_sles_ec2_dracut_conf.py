import pytest


def test_sles_ec2_dracut_conf(host, get_release_value, determine_architecture):
    if determine_architecture() != 'X86_64':
        pytest.skip('Only x86_64 architecture is tested.')

    needed_drivers = {
        '07-aws-type-switch.conf': [
            'ena',
            'virtio',
            'virtio_scsi',
            'xen-blkfront',
            'xen-netfront'
        ],
        '07-nvme.conf': [
            'nvme',
            'nvme-core'
        ]
    }

    version = get_release_value('VERSION')
    assert version

    name = get_release_value('PRETTY_NAME').lower()
    assert name

    base_dracut_config_dir = '/etc/dracut.conf.d/'

    for cfg_filename, expected_drivers in needed_drivers.items():

        dracut_conf = host.file(base_dracut_config_dir + cfg_filename)

        assert dracut_conf.exists
        assert dracut_conf.is_file

        for driver in expected_drivers:
            if (
                driver.startswith('virtio') and
                (
                    version.startswith('15') or
                    version == '12-SP5' or
                    'micro' in name
                )
            ):
                continue
            assert dracut_conf.contains(driver)
