import pytest

@pytest.mark.parametrize('name', [
    'google-guest-agent.service',
    'google-osconfig-agent.service',
    'google-oslogin-cache.timer'
])
def test_sles_gce_running_services(check_service, name, is_sle_micro, get_version):
    if is_sle_micro():
        version = get_version()
        if version is not None and version <= 5.4:
            pytest.skip('Skipping test for SLE Micro < 5.5')

    check_service(name)


@pytest.mark.parametrize('name', [
    'google-startup-scripts.service',
    'google-shutdown-scripts.service',
])
def test_sles_gce_one_shot_services(check_service, host, name, is_sle_micro, get_version):
    if is_sle_micro():
        version = get_version()
        if version is not None and version <= 5.4:
            pytest.skip('Skipping test for SLE Micro < 5.5')

    check_service(name, running=None)

    if host.exists('systemctl'):
        # No clear way to check a service exited successfully using sysvinit
        output = host.run(
            "systemctl show -p Result {0} | sed 's/Result=//g'".format(name)
        )
        assert output.stdout.strip() == 'success'
