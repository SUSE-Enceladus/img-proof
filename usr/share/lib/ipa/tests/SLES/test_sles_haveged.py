def test_sles_haveged(check_service):
    assert check_service('haveged')
