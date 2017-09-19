def test_sles_motd(host, get_release_value):
    motd = host.file('/etc/motd')
    pretty_name = get_release_value('PRETTY_NAME')
    assert pretty_name
    assert motd.contains(pretty_name)
