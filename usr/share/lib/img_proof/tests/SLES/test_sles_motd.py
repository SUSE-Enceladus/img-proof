def test_sles_motd(host, get_release_value):
    motd = host.file('/etc/motd')
    assert motd.exists
    assert motd.is_file

    pretty_name = get_release_value('PRETTY_NAME')
    assert pretty_name

    version = get_release_value('VERSION')
    assert version

    assert (
        motd.contains(pretty_name) or
        motd.contains(
            'SUSE Linux Enterprise Server {0}'.format(
                version.replace('-', ' ')
            )
        )
    )
