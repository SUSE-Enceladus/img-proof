def test_sles_dracut_conf(host):
    needed_drivers = ('ena', 'nvme', 'nvme-core', 'virtio', 'virtio_scsi',
                      'xen-blkfront', 'xen-netfront')
    dracut_conf = host.file('/etc/dracut.conf.d/07-aws-type-switch.conf')
    for driver in needed_drivers:
        assert dracut_conf.contains(driver)
