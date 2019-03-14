def test_sles_motd(host, get_release_value):
    motd = host.file('/etc/motd')
    version = get_release_value('VERSION')
    assert version
    assert motd.contains(
        'SUSE Linux Enterprise Server {0}'.format(
            version.replace('-', ' ')
        )
    )
