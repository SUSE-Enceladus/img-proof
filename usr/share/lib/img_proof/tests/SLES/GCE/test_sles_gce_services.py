import pytest


@pytest.mark.parametrize('name', [
    'google-guest-agent',
    'google-osconfig-agent',
    'google-oslogin-cache.timer'
])
def test_sles_gce_running_services(check_service, name):
    assert check_service(name)


@pytest.mark.parametrize('name', [
    'google-startup-scripts',
    'google-shutdown-scripts',
])
def test_sles_gce_one_shot_services(check_service, host, name):
    assert check_service(name, running=None)

    if host.exists('systemctl'):
        # No clear way to check a service exited successfully using sysvinit
        output = host.run(
            "systemctl show -p Result {0} | sed 's/Result=//g'".format(name)
        )
        assert output.stdout.strip() == 'success'
