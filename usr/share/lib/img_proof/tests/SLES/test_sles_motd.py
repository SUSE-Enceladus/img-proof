import pytest


@pytest.mark.skipinbeta
def test_sles_motd(
    host,
    get_release_value,
    is_byos,
    is_suma_proxy,
    get_variant,
    is_suma,
    get_suma_version
):
    pretty_name = get_release_value('PRETTY_NAME')
    assert pretty_name

    version = get_release_value('VERSION')
    assert version

    variant = get_variant()
    suma_version = get_suma_version()

    if 'hardened' in variant:
        pytest.skip('Unable to validate motd in hardened images.')

    motd_candidates = [
        '/etc/motd',
        '/etc/motd.d/10_header',
        '/usr/lib/motd.d/10_header',
        '/usr/lib/motd.d/05_ext_header',
    ]
    motd = None
    for candidate_path in motd_candidates:
        candidate = host.file(candidate_path)
        if candidate.exists and candidate.size > 0:
            motd = candidate
            break
    if motd is None:
        motd = host.file(motd_candidates[0])

    assert motd.exists
    assert motd.is_file

    assert (
        motd.contains(pretty_name) or
        motd.contains('SUSE Linux Enterprise Server') and
        motd.contains(str(version.replace('-', ' ')))
    )

    # check motd content for all segments
    def contains_registration_tools(motd_file):
        """Checks if any of the registration tools is mentioned in motd"""
        tools = [
            'registercloudguest',
            'SUSEConnect',
            'suseconnect',
            'transactional-update'
        ]
        return any(
            motd_file.contains(tool) for tool in tools
        )

    def registration_tools_found(contain_results):
        return any(contain_results)

    contain_results = []
    if is_suma() and suma_version and float(suma_version) >= 5.2:
        # No registration tools expected in motd for SUMA 5.2 proxy or server
        registration_tools_expected = False
    else:
        # Rest of versions.
        # reg tools mentioned in in motd expected for any BYOS
        # except SUMA Proxy <= 5.1
        registration_tools_expected = is_byos() and not is_suma_proxy()

    motd = host.file('/etc/motd')
    if motd.exists:
        contain_results.append(contains_registration_tools(motd))

    if registration_tools_expected:
        if registration_tools_found(contain_results):
            # reg tools found and expected, test OK
            return
    else:
        if registration_tools_found(contain_results):
            # reg tools found and not expected, test should fail
            assert False

    # Check for every segment under the /usr/lib/motd.d directory
    # if the result of the tests is unknown after checking /etc/motd
    motd_dir = '/usr/lib/motd.d'
    motd_ls_cmd = f'ls {motd_dir}'
    result = host.run(motd_ls_cmd)

    segments = [
        filename for filename in result.stdout.strip().split('\n') if filename
    ]
    for segment in sorted(segments):
        motd = host.file(f'{motd_dir}/{segment}')
        if motd.exists and motd.is_file:
            contain_results.append(contains_registration_tools(motd))

    if registration_tools_expected:
        assert registration_tools_found(contain_results)
    else:
        assert not registration_tools_found(contain_results)
