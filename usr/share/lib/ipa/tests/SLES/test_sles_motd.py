def test_sles_motd(host, GetReleaseValue):
    motd = host.file('/etc/motd')
    pretty_name = GetReleaseValue('PRETTY_NAME')
    assert pretty_name
    assert motd.contains(pretty_name)
