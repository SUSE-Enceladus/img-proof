

def test_sles_lscpu(host):
    result = host.run('lscpu')
    assert result.rc == 0
