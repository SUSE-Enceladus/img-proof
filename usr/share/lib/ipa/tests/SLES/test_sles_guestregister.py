def test_sles_guestregister(CheckService):
    assert CheckService('guestregister.service', running=False)
