import pytest


@pytest.mark.parametrize('name', [
    ('google-accunts-daemon.service'),
    ('google-clock-skew-daemon.service'),
    ('google-instance-setup.service'),
    ('google-ip-forwarding-daemon.service'),
    ('google-shutdown-scripts.service'),
    ('google-startup-scripts.service'),
])
def test_sles_gce_services(CheckService, name):
    assert CheckService(name)
