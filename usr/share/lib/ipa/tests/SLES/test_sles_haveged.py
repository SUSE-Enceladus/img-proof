def test_sles_haveged(CheckService):
    assert CheckService('haveged.service')
