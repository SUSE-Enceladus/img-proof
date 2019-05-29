import pytest


@pytest.mark.parametrize('name', [
    'google-accounts-daemon',
    'google-clock-skew-daemon',
    'google-network-daemon'
])
def test_sles_gce_running_services(check_service, name):
    assert check_service(name)


@pytest.mark.parametrize('name', [
    'google-instance-setup',
    'google-startup-scripts',
    'google-shutdown-scripts'
])
def test_sles_gce_one_shot_services(check_service, host, name):
    assert check_service(name, running=None)

    if host.exists('systemctl'):
        # No clear way to check a service exited successfully using sysvinit
        output = host.run(
            "systemctl show -p Result {0} | sed 's/Result=//g'".format(name)
        )
        assert output.stdout.strip() == 'success'
