def test_sles_multipath_off(host):
    kernel_cmdline = host.file('/proc/cmdline')
    assert kernel_cmdline.contains(' multipath=off ')
