def test_sles_zypper_migration(host):
    result = host.run('sudo zypper migration -n -l')
    assert result.rc == 0
