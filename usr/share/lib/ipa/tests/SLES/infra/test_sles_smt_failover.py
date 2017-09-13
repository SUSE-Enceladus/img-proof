import shlex


def test_sles_smt_failover(GetSMTServerName,
                           GetSMTServers,
                           GetReleaseValue,
                           host,
                           request):
    provider = request.config.getoption('provider')
    region = request.config.getoption('region')

    result = host.run('cat /etc/hosts | grep %s' % GetSMTServerName(provider))
    smt_ip = shlex.split(result.stdout)[0]

    pretty_name = GetReleaseValue('PRETTY_NAME')
    servers = GetSMTServers(pretty_name, provider, region)

    for server in servers:
        if server['ip'] != smt_ip:
            result = host.run(
                "sudo sed -i 's/{current}/{new}/' /etc/hosts".format(
                    current=smt_ip,
                    new=server['ip']
                )
            )
            assert result.rc == 0
            break
