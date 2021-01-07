import pytest

def test_sles_ec2_x86_64_dracut_conf(host):
    needed_drivers = (
        'ena',
        'nvme',
        'nvme-core',
        'virtio',
        'virtio_scsi',
        'xen-blkfront',
        'xen-netfront'
    )
    version = get_release_value('VERSION')
    assert version

    dracut_conf = host.file('/etc/dracut.conf.d/07-aws-type-switch.conf')

    assert dracut_conf.exists
    assert dracut_conf.is_file

    for driver in needed_drivers:
        if (
                driver.startswith('virtio') and
                (version.startswith('15') or version == '12-SP5')
        ):
            continue
        assert dracut_conf.contains(driver)
