def test_sles_azure_infiniband(host):
    hyperv = '/var/lib/hyperv'
    hyperv_dir = host.file(hyperv)

    assert hyperv_dir.exists
    assert hyperv_dir.is_directory

    result = host.run('find {hyperv} ! -path {hyperv} | wc -l'.format(
        hyperv=hyperv
    ))
    assert int(result.stdout) > 0
