def test_sles_guestregister(check_service):
    check_service('guestregister', running=False)
