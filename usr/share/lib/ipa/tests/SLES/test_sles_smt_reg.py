import shlex


def test_sles_smt_reg(check_cloud_register,
                      determine_provider,
                      get_smt_server_name,
                      get_smt_servers,
                      host,
                      request):
    provider = determine_provider()
    region = request.config.getoption('region')

    assert check_cloud_register()

    servers = get_smt_servers(provider, region)
    smt_ips = [server['ip'] for server in servers]

    result = host.run(
        'cat /etc/hosts | grep %s' % get_smt_server_name(provider)
    )
    smt_ip = shlex.split(result.stdout)[0]

    assert smt_ip in smt_ips
