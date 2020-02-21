import pytest
import time


def test_sles_wait_on_registration(host):
    start = time.time()
    end = start + 600

    while time.time() < end:
        result = host.run('systemctl is-active guestregister.service')

        if result.stdout.strip() == 'inactive':
            break
        else:
            time.sleep(10)
    else:
        pytest.fail(
            'Registration did not finish properly for on-demand instance.'
        )
