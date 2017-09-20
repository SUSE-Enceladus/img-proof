import pytest


@pytest.mark.parametrize('name', [
    ('waagent.service'),
])
def test_sles_ec2_services(check_service, name):
    assert check_service(name)
