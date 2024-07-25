import shlex


def test_sles_grow_root(host):
    """
    Ensure root filesystem grows to non default size

    The partitions are slightly different in all images.
    However, there is always a root partition and in Azure
    the boot partition is 1GB.

    All the smaller partitions round to zero and
    therefore they are ignored in calculating size of fs.
    """

    # Get root disk size
    root_part = host.run(
        'findmnt -v -n -f -o SOURCE /'
    ).stdout.strip()

    device_name = host.run(
        'lsblk -npo pkname {part}'.format(part=root_part)
    ).stdout.strip()

    result = host.run(
        'lsblk -ndo size {device}'.format(device=device_name)
    ).stdout.strip()

    try:
        disk_size = float(result.replace('G', ''))
        unit = 'G'
    except ValueError:
        disk_size = float(result.replace('T', ''))
        unit = 'T'

    # Get root partition size
    result = host.run(
        'df -B{unit} {part} | sed 1D'.format(unit=unit, part=root_part)
    ).stdout.strip()

    root_size = shlex.split(result)[1]  # Filesystem 1G-blocks
    root_size = float(root_size.replace(unit, ''))

    # Get boot partition size
    boot_part = host.run('findmnt -v -n -f -o SOURCE /boot').stdout.strip()

    if boot_part:
        # Some images have a separate boot partition that is >= 1G
        result = host.run(
            'df -B{unit} {part} | sed 1D'.format(unit=unit, part=boot_part)
        ).stdout.strip()

        boot_size = shlex.split(result)[1]  # Filesystem 1G-blocks
        boot_size = float(boot_size.replace(unit, ''))
    else:
        boot_size = 0

    # Get /var partition size
    var_part = host.run('findmnt -v -n -f -o SOURCE /var').stdout.strip()

    if var_part and var_part != root_part:
        # Some images have a separate /var partition that is >= 1G
        result = host.run(
            'df -B{unit} {part} | sed 1D'.format(unit=unit, part=var_part)
        ).stdout.strip()

        var_size = shlex.split(result)[1]  # Filesystem 1G-blocks
        var_size = float(var_size.replace(unit, ''))
    else:
        var_size = 0

    total_size = root_size + boot_size + var_size

    # Rounding can lead to small discrepancies
    assert (((disk_size - 1) <= total_size) and (total_size <= (disk_size + 1)))
