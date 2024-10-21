import ipaddress
import pytest
import shlex


def test_sles_smt_reg(
    check_cloud_register,
    determine_provider,
    get_smt_server_name,
    get_smt_servers,
    host
):
    provider = determine_provider()

    # ensure instance registered successfully
    assert check_cloud_register()

    # ensure the correct smt/rmt ip is used
    servers = get_smt_servers(provider)
    smt_ips = list(filter(None, [server['ip'] for server in servers]))
    smt_ips += list(filter(None, [server['ipv6'] for server in servers]))

    result = host.run(
        'cat /etc/hosts | grep %s' % get_smt_server_name(provider)
    )
    smt_ip = shlex.split(result.stdout)[0]

    for server_ip in smt_ips:
        if ipaddress.ip_address(smt_ip) == ipaddress.ip_address(server_ip):
            break
    else:
        pytest.fail(f'RMT Server not found {smt_ip}')

    # ensure region hint is in log
    cloud_register_log = host.file('/var/log/cloudregister')
    assert cloud_register_log.contains(
        'INFO:Region server arguments: ?regionHint='
    )
