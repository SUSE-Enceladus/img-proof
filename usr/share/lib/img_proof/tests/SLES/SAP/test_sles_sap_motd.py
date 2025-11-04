import pytest


@pytest.mark.skipinbeta
def test_sles_sap_motd(host, get_release_value, get_variant, get_version):
    motd = host.file('/etc/motd')

    if not motd.exists:
        motd = host.file('/usr/lib/motd.d/10_header')

    assert motd.exists
    assert motd.is_file

    variant = get_variant()
    version = get_version()

    if (
        'hardened' in variant or
        # SAP is hardened by default in >=16.0
        version >= 16.0
    ):
        pytest.skip(
            'Unable to validate motd in hardened images or SAP images >= 16.0.'
        )

    assert motd.contains('for SAP Applications')
