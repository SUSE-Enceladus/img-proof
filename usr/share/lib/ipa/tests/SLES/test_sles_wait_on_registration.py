import pytest
import time


def test_sles_wait_on_registration(host):
    start = time.time()
    end = start + 600

    while time.time() < end:
        result = host.run('pgrep registercloud')

        if not result.stdout.strip():
            break
        else:
            time.sleep(10)
    else:
        pytest.fail(
            'Registration did not finish properly for on-demand instance.'
        )
