def test_sles_gce_sev(host):
    expected = 'SEV'
    output = host.run('dmesg')
    assert expected in output.stdout.strip()
