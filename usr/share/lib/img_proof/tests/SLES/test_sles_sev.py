def test_sles_sev(host):
    expected = 'SEV'

    with host.sudo():
        output = host.run('dmesg')

    assert expected in output.stdout.strip()
