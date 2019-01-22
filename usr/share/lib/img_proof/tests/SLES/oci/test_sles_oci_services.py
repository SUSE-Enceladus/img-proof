import pytest


@pytest.mark.parametrize('name', [
    ('cloud-init-local'),
    ('cloud-init'),
    ('cloud-config'),
    ('cloud-final')
])
def test_sles_oci_services(check_service, host, name):
    assert check_service(name, running=None)

    if host.exists('systemctl'):
        # No clear way to check a service exited successfully using sysvinit
        output = host.run(
            "systemctl show -p Result {0} | sed 's/Result=//g'".format(name)
        )
        assert output.stdout.strip() == 'success'
