

def test_sles_repos(check_zypper_repo,
                    determine_provider,
                    get_release_value,
                    get_sles_repos,
                    is_sles_sap):
    provider = determine_provider()
    version = get_release_value('VERSION')
    sap = is_sles_sap()

    if sap:
        version += '-SAP'

    missing_repos = []
    for repo in get_sles_repos(version):
        result = check_zypper_repo(
            ''.join([
                'SMT-http_smt-{provider}_susecloud_net:'.format(
                    provider=provider
                ),
                repo
            ])
        )
        if not result:
            missing_repos.append(
                ''.join([
                    'SMT-http_smt-{provider}_susecloud_net:'.format(
                        provider=provider
                    ),
                    repo
                ])
            )

    if missing_repos:
        raise Exception(
            'Missing Repos: \n{0}'.format('\n'.join(missing_repos))
        )
