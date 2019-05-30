def test_sles_azure_accel_networking(host):
    has_mellanox_hw = 'Mellanox' in host.run('sudo lspci').stdout

    if has_mellanox_hw:
        assert 'mlx' in host.run('sudo lsmod').stdout
