def test_sles_hostname(host):
    assert host.system_info.hostname != 'linux'
