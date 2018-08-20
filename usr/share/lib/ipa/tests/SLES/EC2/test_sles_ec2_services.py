import pytest


@pytest.mark.parametrize('name', [
    ('cloud-init-local'),
    ('cloud-init'),
    ('cloud-config'),
    ('cloud-final')
])
def test_sles_ec2_services(check_service, name):
    assert check_service(name)
