import pytest


def test_passing():
    assert True


def test_another_pass():
    assert True


@pytest.mark.failtest
def test_failing():
    assert False
