import shlex


def test_sles_grow_root(host):
    """
    Ensure root filesystem grows to non default size
    """

    # Get root disk size
    root_part = host.run('findmnt -n -f -o SOURCE /').stdout.strip()

    device_name = host.run(
        'lsblk -npo pkname {part}'.format(part=root_part)
    ).stdout.strip()

    result = host.run(
        'lsblk -ndo size {device}'.format(device=device_name)
    ).stdout.strip()

    disk_size = int(result.replace('G', ''))

    # Get root partition size
    result = host.run(
        'df -BG {part} | sed 1D'.format(part=root_part)
    ).stdout.strip()

    root_size = shlex.split(result)[1]  # Filesystem 1G-blocks
    root_size = int(root_size.replace('G', ''))

    # Get boot partition size
    boot_part = host.run('findmnt -n -f -o SOURCE /boot').stdout.strip()

    if boot_part:
        # Some images have a separate boot partition
        result = host.run(
            'df -BG {part} | sed 1D'.format(part=boot_part)
        ).stdout.strip()

        boot_size = shlex.split(result)[1]  # Filesystem 1G-blocks
        boot_size = int(boot_size.replace('G', ''))
    else:
        boot_size = 0

    assert root_size + boot_size == disk_size
