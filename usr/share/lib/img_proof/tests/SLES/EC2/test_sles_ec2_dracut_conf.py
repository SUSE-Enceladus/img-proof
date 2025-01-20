import pytest
import shlex


def test_sles_ec2_dracut_conf(host, get_release_value, determine_architecture):
    if determine_architecture() != 'X86_64':
        pytest.skip('Only x86_64 architecture is tested.')

    needed_drivers = [
        'ena',
        'virtio',
        'virtio_scsi',
        'xen-blkfront',
        'xen-netfront',
        'nvme',
        'nvme-core'
    ]

    base_dracut_config_dirs = [
        '/usr/lib/dracut/dracut.conf.d/',
        '/etc/dracut.conf.d/'
    ]
    config_files = []
    for config_dir in base_dracut_config_dirs:
        cfg_dir = host.file(config_dir)
        if not cfg_dir.exists or not cfg_dir.is_directory:
            continue

        config_dir_ls = host.run(f'ls {config_dir}').stdout.strip()
        config_files_in_dir = shlex.split(config_dir_ls)
        for config_file in config_files_in_dir:
            config_files.append(config_dir + config_file)

    version = get_release_value('VERSION')
    assert version

    name = get_release_value('PRETTY_NAME').lower()
    assert name

    for driver in needed_drivers:
        if (
            driver.startswith('virtio') and
            (
                version.startswith('15') or
                version == '12-SP5' or
                'micro' in name
            )
        ):
            continue

        found = False
        for cfg_filename in config_files:
            dracut_conf = host.file(cfg_filename)
            if (
                dracut_conf.exists and
                dracut_conf.is_file and
                dracut_conf.contains(driver)
            ):
                found = True
                break
        assert found
