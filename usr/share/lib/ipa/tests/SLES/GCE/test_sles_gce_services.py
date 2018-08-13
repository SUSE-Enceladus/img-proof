import pytest


@pytest.mark.parametrize('name', [
    'google-accounts-daemon.service',
    'google-clock-skew-daemon.service',
    'google-network-daemon.service',
    'google-shutdown-scripts.service'
])
def test_sles_gce_running_services(check_service, name):
    assert check_service(name)


@pytest.mark.parametrize('name', [
    'google-instance-setup.service',
    'google-startup-scripts.service',
    'google-shutdown-scripts.service'  # Exits but remains active
])
def test_sles_gce_one_shot_services(host, name):
    service = host.service(name)
    assert service.is_enabled

    output = host.run(
        "systemctl show -p Result {0} | sed 's/Result=//g'".format(name)
    )
    assert output.stdout.strip() == 'success'
