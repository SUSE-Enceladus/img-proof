import shlex


def test_sles_root_pass(host):
    # Ensure root does not have a password
    result = host.run(
        'sudo passwd -S root'
    )
    assert shlex.split(result.stdout.strip())[1] in ['L', 'LK', 'NP']
