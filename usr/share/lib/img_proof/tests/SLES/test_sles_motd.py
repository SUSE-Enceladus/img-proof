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

    # check motd content for all segments
    def contains_registration_tools(motd_file):
        """Checks if any of the registration tools is mentioned in motd"""
        return (
            motd_file.contains('registercloudguest') or
            motd_file.contains('SUSEConnect') or
            motd_file.contains('transactional-update')
        )

    contain_results = []

    motd = host.file('/etc/motd')
    if motd.exists:
        contain_results.append(contains_registration_tools(motd))
    else:
        # check for every segment under the motd.d dir
        motd_dir = '/usr/lib/motd.d'
        motd_ls_cmd = f'ls {motd_dir}'
        result = host.run(motd_ls_cmd)

        segments = [filename for filename in result.stdout.strip().split('\n') if filename]  # NOQA
        for segment in sorted(segments):
            motd = host.file(f'{motd_dir}/{segment}')
            if motd.exists and motd.is_file:
                contain_results.append(contains_registration_tools(motd))

    if is_byos() and not is_suma_proxy():
        assert contain_results and any(contain_results)
    else:
        assert contain_results and not any(contain_results)
