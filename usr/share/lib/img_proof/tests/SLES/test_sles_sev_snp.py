def test_sles_sev_snp(host):
    expected = 'SEV-SNP'

    with host.sudo():
        output = host.run('dmesg')

    assert expected in output.stdout.strip()
