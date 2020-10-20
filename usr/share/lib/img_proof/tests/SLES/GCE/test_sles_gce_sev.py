def test_sles_gce_sev(host):
    expected = 'AMD Secure Encrypted Virtualization (SEV) active'
    output = host.run('dmesg | grep SEV')
    assert expected in output.stdout.strip()
