import json
import shlex

from subprocess import PIPE, Popen


def test_sles_smt_reg(GetReleaseValue, host, request):
    provider = request.config.getoption('provider')
    region = request.config.getoption('region')

    smt_server_name = 'smt-{}.susecloud.net'.format(provider)

    client_conf = host.file('/etc/regionserverclnt.cfg')
    assert not client_conf.contains('failed')

    pretty_name = GetReleaseValue('PRETTY_NAME')
    if 'SAP' in pretty_name:
        smt_type = 'smt-sap'
    else:
        smt_type = 'smt-sles'

    if provider == 'azure':
        provider = 'microsoft'
    elif provider == 'ec2':
        provider = 'amazon'
    elif provider == 'gce':
        provider = 'google'
    else:
        raise Exception('Provider %s unknown' % provider)

    cmd = 'pint {provider} servers --region="{region}" --smt --json ' \
        '--filter="type~{smt_type}"'.format(
            provider=provider,
            region=region,
            smt_type=smt_type
        )

    with Popen(shlex.split(cmd), stdout=PIPE) as proc:
        output = json.loads(proc.stdout.read())

    servers = [server['ip'] for server in output['servers']]

    result = host.run('cat /etc/hosts | grep %s' % smt_server_name)
    smt_ip = shlex.split(result.stdout)[0]

    assert smt_ip in servers
