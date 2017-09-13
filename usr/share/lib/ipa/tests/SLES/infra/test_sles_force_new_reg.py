def test_sles_force_new_reg(CheckCloudRegister, host):
    host.run("sudo sh -c ': > /var/log/cloudregister'")
    result = host.run('sudo registsercloudguest --force-new')
    assert result.rc == 0
    assert CheckCloudRegister()
