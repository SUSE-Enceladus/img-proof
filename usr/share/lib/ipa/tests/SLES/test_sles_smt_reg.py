import shlex


def test_sles_smt_reg(CheckCloudRegister,
                      GetReleaseValue,
                      GetSMTServerName,
                      GetSMTServers,
                      host,
                      request):
    provider = request.config.getoption('provider')
    region = request.config.getoption('region')

    assert CheckCloudRegister()

    pretty_name = GetReleaseValue('PRETTY_NAME')
    servers = GetSMTServers(pretty_name, provider, region)
    smt_ips = [server['ip'] for server in servers]

    result = host.run('cat /etc/hosts | grep %s' % GetSMTServerName(provider))
    smt_ip = shlex.split(result.stdout)[0]

    assert smt_ip in smt_ips
