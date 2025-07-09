import pytest


@pytest.mark.skipinbeta
def test_sles_sap_motd(host, get_release_value, get_variant):
    motd = host.file('/etc/motd')
    assert motd.exists
    assert motd.is_file

    variant = get_variant()
    if 'hardened' in variant:
        pytest.skip('Unable to validate motd in hardened images.')

    assert motd.contains('for SAP Applications')
