def test_sles_force_new_reg(check_cloud_register, host):
    host.run("sudo sh -c ': > /var/log/cloudregister'")
    result = host.run('sudo registercloudguest --force-new')
    assert result.rc == 0
    assert check_cloud_register()
