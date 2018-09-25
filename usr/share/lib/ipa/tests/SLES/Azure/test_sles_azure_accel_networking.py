def test_sles_azure_accel_networking(host):
    result = host.run('sudo lspci')
    assert 'Mellanox' in result.stdout
