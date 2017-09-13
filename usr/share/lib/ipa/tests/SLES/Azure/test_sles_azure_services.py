import pytest


@pytest.mark.parametrize('name', [
    ('waagent.service'),
])
def test_sles_ec2_services(CheckService, name):
    assert CheckService(name)
