import pytest


def test_sles_haveged(check_service, get_version, is_sle_micro):
    version = get_version()
    assert version

    if version != 12.5:
        pytest.skip('haveged service is only in 12-SP5 images')

    if is_sle_micro() and version >= 6.0:
        pytest.skip('haveged service is not in micro 6+ images')

    check_service('haveged')
