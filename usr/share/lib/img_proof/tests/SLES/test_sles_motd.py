import pytest


@pytest.mark.skipinbeta
def test_sles_motd(host, get_release_value, is_byos, is_suma_proxy):
    motd = host.file('/etc/motd')

    if not motd.exists:
        motd = host.file('/usr/lib/motd.d/10_header')

    assert motd.exists
    assert motd.is_file

    pretty_name = get_release_value('PRETTY_NAME')
    assert pretty_name

    version = get_release_value('VERSION')
    assert version

    variant = get_release_value('VARIANT_ID') or ''

    if 'hardened' in variant:
        pytest.skip('Unable to validate motd in hardened images.')

    assert (
        motd.contains(pretty_name) or
        motd.contains(
            'SUSE Linux Enterprise Server {0}'.format(
                version.replace('-', ' ')
            )
        )
    )

    if is_byos() and not is_suma_proxy():
        assert (
            motd.contains('registercloudguest') or
            motd.contains('SUSEConnect') or
            motd.contains('transactional-update')
        )
    else:
        assert (
            not motd.contains('registercloudguest') and
            not motd.contains('SUSEConnect') and
            not motd.contains('transactional-update')
        )
