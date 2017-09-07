def test_sles_install_migration(InstallZypperPackage):
    assert InstallZypperPackage('zypper-migration-plugin')
