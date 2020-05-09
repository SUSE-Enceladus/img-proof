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
    smt_ips = [server['ip'] for server in servers]

    result = host.run(
        'cat /etc/hosts | grep %s' % get_smt_server_name(provider)
    )
    smt_ip = shlex.split(result.stdout)[0]

    assert smt_ip in smt_ips

    # ensure region hint is in log
    cloud_register_log = host.file('/var/log/cloudregister')
    assert cloud_register_log.contains(
        'INFO:Region server arguments: ?regionHint='
    )
