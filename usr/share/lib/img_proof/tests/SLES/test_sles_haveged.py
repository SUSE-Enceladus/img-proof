import pytest


def test_sles_haveged(check_service, get_release_value, is_sle_micro):
    version = get_release_value('VERSION')
    assert version

    have_haveged = ('12-SP5', '15-SP3', '15-SP4', '15-SP5')
    if version not in have_haveged:
        pytest.skip('haveged service is not in SP6+ images')

    if is_sle_micro() and float(version) >= 6.0:
        pytest.skip('haveged service is not in micro 6+ images')

    assert check_service('haveged')
