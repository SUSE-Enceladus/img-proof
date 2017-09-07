import json
import shlex

from susepubliccloudinfoclient import infoserverrequests


def test_sles_smt_reg(GetReleaseValue, host, request):
    provider = request.config.getoption('provider')
    region = request.config.getoption('region')

    smt_server_name = 'smt-{}.susecloud.net'.format(provider)

    client_log = host.file('/var/log/cloudregister')
    assert not client_log.contains('ERROR')
    assert not client_log.contains('failed')

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

    output = json.loads(
        infoserverrequests.get_server_data(
            provider,
            'smt',
            'json',
            region,
            'type~{smt_type}'.format(smt_type=smt_type)
        )
    )

    servers = [server['ip'] for server in output['servers']]

    result = host.run('cat /etc/hosts | grep %s' % smt_server_name)
    smt_ip = shlex.split(result.stdout)[0]

    assert smt_ip in servers
