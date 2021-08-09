import shlex


def test_sles_grow_root(host):
    # Ensure root filesystem grows to non default size
    result = host.run('df -h /')
    size = shlex.split(result.stdout.strip().split('\n')[1])[1]
    assert size in ('49G', '50G')  # Azure has 1GB boot partition
