import shlex


def test_sles_smt_reg(check_cloud_register,
                      get_release_value,
                      get_smt_server_name,
                      get_smt_servers,
                      host,
                      request):
    provider = request.config.getoption('provider')
    region = request.config.getoption('region')

    assert check_cloud_register()

    pretty_name = get_release_value('PRETTY_NAME')
    servers = get_smt_servers(pretty_name, provider, region)
    smt_ips = [server['ip'] for server in servers]

    result = host.run(
        'cat /etc/hosts | grep %s' % get_smt_server_name(provider)
    )
    smt_ip = shlex.split(result.stdout)[0]

    assert smt_ip in smt_ips
