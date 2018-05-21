def test_sles_root_pass(host):
    # Ensure root does not have a password
    result = host.run(
        "sudo getent shadow | grep '^root[^:]*:.\?:' | cut -d: -f1"
    )
    assert result.stdout.strip() == 'root'
