def test_sles_tdx(host):
    expected = 'Intel TDX'

    with host.sudo():
        output = host.run('dmesg')

    assert expected in output.stdout.strip()
