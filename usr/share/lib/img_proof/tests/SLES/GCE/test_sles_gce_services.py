import pytest


@pytest.mark.parametrize('name', [
    'google-guest-agent'
])
def test_sles_gce_running_services(check_service, name):
    assert check_service(name)


@pytest.mark.parametrize('name', [
    'google-startup-scripts',
    'google-shutdown-scripts',
    'google-optimize-local-ssd',
    'google-oslogin-cache',
    'google-set-multiqueue'
])
def test_sles_gce_one_shot_services(check_service, host, name):
    assert check_service(name, running=None)

    if host.exists('systemctl'):
        # No clear way to check a service exited successfully using sysvinit
        output = host.run(
            "systemctl show -p Result {0} | sed 's/Result=//g'".format(name)
        )
        assert output.stdout.strip() == 'success'
