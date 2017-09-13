

def test_sles_force_new_smt_reg(CheckCloudRegister,
                                GetReleaseValue,
                                GetSMTServers,
                                host,
                                request):
    certs_dir = '/var/lib/regionService/certs/'
    provider = request.config.getoption('provider')
    region = request.config.getoption('region')

    host.run("sudo sh -c ': > /var/log/cloudregister'")
    result = host.run('cat /etc/regionserverclnt.cfg | grep regionsrv')
    region_srv = result.stdout.split('=')[-1].strip().split(',')[-1]

    result = host.run(
        'openssl x509 -noout -fingerprint -sha1 -inform pem -in %s'
        % ''.join([certs_dir, region_srv, '.pem'])
    )
    fingerprint = result.stdout.split('=')[-1]

    pretty_name = GetReleaseValue('PRETTY_NAME')
    servers = GetSMTServers(pretty_name, provider, region)

    result = host.run(
        'sudo registercloudguest --force-new --smt-ip={ip} '
        '--smt-fqdn={fqdn} --smt-fp={fp}'.format(
            ip=servers[0]['ip'],
            fqdn=servers[0]['name'],
            fp=fingerprint
        )
    )

    assert result.rc == 0
    assert CheckCloudRegister()
