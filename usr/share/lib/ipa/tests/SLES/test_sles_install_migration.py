def test_sles_install_migration(InstallZypperPackage):
    result = InstallZypperPackage('zypper-migration-plugin')
    assert result == 0
