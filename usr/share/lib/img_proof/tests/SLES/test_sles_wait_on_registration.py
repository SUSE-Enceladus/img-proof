import pytest
import time


def test_sles_wait_on_registration(host):
    start = time.time()
    end = start + 600

    while time.time() < end:
        result = host.run('systemctl is-active guestregister.service')
        status = result.stdout.strip()

        if status == 'inactive':
            break
        elif status == 'failed':
            pytest.fail(
                'Registration failed for on-demand instance.'
            )
        else:
            time.sleep(10)
    else:
        pytest.fail(
            'Registration did not finish properly for on-demand instance.'
        )
