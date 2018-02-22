def test_sles_hostname(host):
    result = host.run('hostname')
    assert result.stdout.strip() != 'linux'
