def test_sles_hostname(host):
    result = host.run('hostname')
    print('*** %s ***' % result.stdout.strip())
    assert result.stdout.strip() != 'linux'
