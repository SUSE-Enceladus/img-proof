import pytest


@pytest.mark.parametrize('name', [
    ('cloud-init-local.service'),
    ('cloud-init.service'),
    ('cloud-config.service'),
    ('cloud-final.service')
])
def test_sles_ec2_services(check_service, name):
    assert check_service(name)
