def test_sles_multipath_off(host):
    kernel_cmdline = host.run('cat /proc/cmdline')
    args = kernel_cmdline.stdout.split()
    assert 'multipath=off' in args
