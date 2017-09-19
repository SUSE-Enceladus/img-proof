def test_sles_guestregister(check_service):
    assert check_service('guestregister.service', running=False)
