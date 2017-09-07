def test_sles_zypper_migration(host):
    result = host.run('sudo zypper -n migration')
    assert result.rc
