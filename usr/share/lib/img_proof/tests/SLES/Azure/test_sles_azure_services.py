import pytest


@pytest.mark.parametrize('name', [
    ('waagent.service'),
])
def test_sles_azure_running_services(check_service, name):
    check_service(name)


@pytest.mark.parametrize('name', [
    ('cloud-init-local.service'),
    ('cloud-init.service'),
    ('cloud-config.service'),
    ('cloud-final.service')
])
def test_sles_azure_one_shot_services(check_service, host, name):
    check_service(name, running=None)

    if host.exists('systemctl'):
        # No clear way to check a service exited successfully using sysvinit
        output = host.run(
            "systemctl show -p Result {0} | sed 's/Result=//g'".format(name)
        )
        assert output.stdout.strip() == 'success'
