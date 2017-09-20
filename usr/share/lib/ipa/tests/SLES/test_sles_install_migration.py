def test_sles_install_migration(install_zypper_package):
    result = install_zypper_package('zypper-migration-plugin')
    assert result == 0
